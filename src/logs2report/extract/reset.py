"""Flujo de reseteo de contraseña en ADManager (users_admin/resetuser).

El resultado sale de dos entradas: el POST a ResetPwd, que marca
updated_at, y la 'ADM-Raw response', cuyo body es repr de Python.
"""

import re

from ..reader import Operation
from .common import Flow, Outcome, find_entry, parse_literal

_ADM_RESPONSE = "ADM-Raw response"
_BODY = re.compile(r"body: (\[.*?\])\s*$", re.DOTALL)
_STATUS_CODE = re.compile(r"\|\s*status:\s*(\d{3})\s*\|")


def _parse_body(content: str) -> dict | None:
    """Primer elemento del body, o None si falta o no es válido."""
    match = _BODY.search(content)
    if not match:
        return None
    try:
        body = parse_literal(match.group(1))
    except ValueError:
        return None
    if isinstance(body, list) and body and isinstance(body[0], dict):
        return body[0]
    return None


def parse_outcome(operation: Operation) -> Outcome:
    """updated_at, status y mensaje desde ResetPwd y la respuesta de ADManager."""
    post = find_entry(operation, "HTTP Request: POST", "ResetPwd")
    if post is None:
        raise ValueError("No se encontró el POST a ResetPwd")

    for entry in operation:
        content = entry["content"]
        if _ADM_RESPONSE not in content:
            continue
        response = _parse_body(content)
        if response is None:
            continue
        if response.get("status") is None:
            raise ValueError("La respuesta de ADManager no trae status")

        code = _STATUS_CODE.search(content)
        return Outcome(
            updated_at=post["timestamp"],
            status=str(response["status"]),
            message=str(response.get("statusMessage") or ""),
            status_code=code.group(1) if code else None,
        )

    raise ValueError("No se encontró una respuesta válida de ADManager")


RESET = Flow(
    endpoint="users_admin/resetuser",
    action="resetuser",
    system="ADManager",
    requester_param="sAMAccountName_requester",
    target_param="sAMAccountName_target",
    target_lookup="sam_account_name",
    parse_outcome=parse_outcome,
)
