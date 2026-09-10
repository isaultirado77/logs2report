"""Lo que comparten todos los flujos.

Cada flujo (reset, register) sigue las mismas tres etapas:
solicitud -> usuarios en ADManager -> resultado. Lo que varía entre
flujos se declara en un Flow; todo lo demás vive aquí.
"""

import ast
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from ..models import ReportRow
from ..reader import LogEntry, Operation

ADMANAGER_SEARCH = "ADManagerRawClient.get_users_list_info"
_RAW_RESPONSE = re.compile(
    r"Raw Response: (\{.*?\})\s*,?\s*Raw status_code:", re.DOTALL
)


@dataclass(frozen=True)
class Request:
    """La solicitud que abre la operación."""

    timestamp: str
    requester: str
    target: str


@dataclass(frozen=True)
class User:
    """Un usuario según ADManager. Vacío si no se encontró."""

    sam_account_name: str = ""
    employee_id: str = ""
    first_name: str = ""
    last_name: str = ""
    office: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass(frozen=True)
class Outcome:
    """El resultado de la operación en el sistema destino."""

    updated_at: str
    status: str
    message: str
    status_code: str | None

    @property
    def result(self) -> str:
        return f"{self.status} / {self.message}"


UserField = Literal["sam_account_name", "employee_id"]


@dataclass(frozen=True)
class Flow:
    """Lo que distingue a un flujo de otro."""

    endpoint: str
    action: str
    system: str
    requester_param: str
    target_param: str
    target_lookup: UserField
    parse_outcome: Callable[[Operation], Outcome]

    def applies_to(self, operation: Operation) -> bool:
        return find_entry(operation, self.endpoint) is not None


def find_entry(operation: Operation, *markers: str) -> LogEntry | None:
    """Primera entrada cuyo contenido incluye todos los marcadores."""
    return next(
        (e for e in operation if all(m in e["content"] for m in markers)),
        None,
    )


def parse_literal(text: str) -> Any:
    """Evalúa un repr de Python; cualquier fallo se reporta como ValueError."""
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError, TypeError) as e:
        raise ValueError(f"repr de Python inválido: {e}") from e


def find_user(users: list[User], field: UserField, value: str) -> User:
    """Usuario cuyo campo coincide con el valor, o un User vacío."""
    return next((u for u in users if getattr(u, field) == value), User())


def _text(value: object) -> str:
    return "" if value is None else str(value)


def parse_request(operation: Operation, flow: Flow) -> Request:
    """Timestamp, requester y target desde la entrada con el endpoint."""
    entry = find_entry(operation, flow.endpoint)
    if entry is None:
        raise ValueError(f"No se encontró la solicitud a {flow.endpoint}")

    def param(name: str) -> str:
        match = re.search(rf'{re.escape(name)}=([^&\s"]+)', entry["content"])
        if not match:
            raise ValueError(f"Falta el parámetro {name} en la solicitud")
        return match.group(1)

    return Request(
        timestamp=entry["timestamp"],
        requester=param(flow.requester_param),
        target=param(flow.target_param),
    )


def parse_users(operation: Operation) -> list[User]:
    """Usuarios devueltos por las búsquedas en ADManager.

    Hay dos búsquedas por operación, en orden no estable: nunca se casa
    por posición, se busca por campo con find_user. El payload es JSON
    válido tras 'Raw Response: '.
    """
    users: dict[str, User] = {}
    for entry in operation:
        if ADMANAGER_SEARCH not in entry["content"]:
            continue
        match = _RAW_RESPONSE.search(entry["content"])
        if not match:
            continue
        try:
            found = json.loads(match.group(1)).get("UsersList")
        except json.JSONDecodeError:
            continue
        if not isinstance(found, list) or not found or not isinstance(found[0], dict):
            continue

        raw = found[0]
        sam = _text(raw.get("SAM_ACCOUNT_NAME"))
        if not sam:
            continue
        users[sam] = User(
            sam_account_name=sam,
            employee_id=_text(raw.get("EMPLOYEE_ID")),
            first_name=_text(raw.get("FIRST_NAME")),
            last_name=_text(raw.get("LAST_NAME")),
            office=_text(raw.get("OFFICE")),
        )
    return list(users.values())


def build_row(flow: Flow, operation_id: str, operation: Operation) -> ReportRow:
    """Recorre las tres etapas y arma la fila del reporte."""
    request = parse_request(operation, flow)
    users = parse_users(operation)
    outcome = flow.parse_outcome(operation)

    requester = find_user(users, "sam_account_name", request.requester)
    target = find_user(users, flow.target_lookup, request.target)

    return ReportRow(
        timestamp=request.timestamp,
        updated_at=outcome.updated_at,
        operation_id=operation_id,
        requester=request.requester,
        target=request.target,
        action=flow.action,
        system=flow.system,
        requester_name=requester.full_name,
        target_name=target.full_name,
        requester_office=requester.office,
        target_office=target.office,
        status_code=outcome.status_code,
        result=outcome.result,
    )
