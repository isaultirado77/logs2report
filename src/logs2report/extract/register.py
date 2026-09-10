"""Flujo de alta de usuario en SAP (sap/register_user).

El requester llega como sAMAccountName, pero el target como employeeID.
El resultado sale de dos entradas: el POST a segMttoUsuario, que marca
updated_at y trae el código HTTP, y la 'SAP raw response', que es repr
de Python.
"""

import re

from ..reader import Operation
from .common import Flow, Outcome, find_entry, parse_literal

_SAP_POST = "RESTAdapter/segMttoUsuario"
_SAP_RESPONSE = "SAP raw response:"
_HTTP_CODE = re.compile(r'"HTTP/1\.1 (\d{3})')
_PASSWORD = re.compile(
    r"\s*Contrase(ñ|n)a temporal:.*$", re.IGNORECASE | re.DOTALL
)


def _redact_password(message: str) -> str:
    """Quita la contraseña temporal que SAP incluye en su mensaje."""
    return _PASSWORD.sub("", message)


def _parse_response(content: str) -> dict | None:
    """Cuerpo de la respuesta de SAP, o None si falta o no es válido.

    Forma esperada: {'MT_RespAltaUsrResetPwd': {'Estatus': ..., 'Mensaje': ...}}
    """
    start = content.find(_SAP_RESPONSE)
    if start == -1:
        return None
    try:
        data = parse_literal(content[start + len(_SAP_RESPONSE):].strip())
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    response = next(iter(data.values()), {})
    return response if isinstance(response, dict) else None


def parse_outcome(operation: Operation) -> Outcome:
    """updated_at, código HTTP, estatus y mensaje desde el POST a SAP."""
    post = find_entry(operation, "HTTP Request: POST", _SAP_POST)
    if post is None:
        raise ValueError("No se encontró el POST a SAP")

    for entry in operation:
        response = _parse_response(entry["content"])
        if response is None:
            continue
        if response.get("Estatus") is None:
            raise ValueError("La respuesta de SAP no trae Estatus")

        code = _HTTP_CODE.search(post["content"])
        return Outcome(
            updated_at=post["timestamp"],
            status=str(response["Estatus"]),
            message=_redact_password(str(response.get("Mensaje") or "")),
            status_code=code.group(1) if code else None,
        )

    raise ValueError("No se encontró una respuesta válida de SAP")


REGISTER = Flow(
    endpoint="sap/register_user",
    action="register_user",
    system="SAP",
    requester_param="requester_username",
    target_param="target_employee_id",
    target_lookup="employee_id",
    parse_outcome=parse_outcome,
)