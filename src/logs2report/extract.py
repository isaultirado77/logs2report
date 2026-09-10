import re
import json
import ast
from .models import ResetRecord

RESET_ENDPOINT = "users_admin/resetuser"


def is_reset_operation(operation) -> bool:
    """¿La operación contiene una solicitud a users_admin/resetuser?"""
    if not operation:
        return False
    for record in operation:
        if RESET_ENDPOINT in record['content']:
            return True
    return False


def _parse_request(operation) -> dict:
    """timestamp, requester y target desde la línea de entrada."""
    # Encontrar el registro con users_admin/resetuser
    request_record = None
    for record in operation:
        if RESET_ENDPOINT in record['content']:
            request_record = record
            break

    if not request_record:
        raise ValueError("No reset request found in operation")

    timestamp = request_record['timestamp']
    content = request_record['content']

    # Extraer requester y target
    # Patrón: sAMAccountName_requester=<value> y sAMAccountName_target=<value>
    requester_match = re.search(r'sAMAccountName_requester=([^&\s"]+)', content)
    target_match = re.search(r'sAMAccountName_target=([^&\s"]+)', content)

    if not requester_match or not target_match:
        raise ValueError("Could not extract requester or target from request")

    return {
        'timestamp': timestamp,
        'requester': requester_match.group(1),
        'target': target_match.group(1),
    }


def _parse_admanager_users(operation) -> dict[str, dict]:
    """Datos de ADManager indexados por SAM_ACCOUNT_NAME.

    Dos consultas por operación, en orden no estable: nunca casar por
    posición. El payload es JSON válido tras 'Raw Response: '.
    Devuelve FIRST_NAME, LAST_NAME y OFFICE (str, conserva cero inicial).
    """
    users = {}

    # Buscar registros ADManagerRawClient que contienen JSON de respuesta
    for record in operation:
        if 'ADManagerRawClient.get_users_list_info_from_admanager invoked' in record['content']:
            # Extraer JSON desde "Raw Response: "
            content = record['content']
            raw_response_match = re.search(r'Raw Response: (\{.*?\})\s*,?\s*Raw status_code:', content, re.DOTALL)

            if not raw_response_match:
                continue

            try:
                json_str = raw_response_match.group(1)
                response_data = json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                continue

            # Extraer datos de UsersList
            if 'UsersList' not in response_data or not response_data['UsersList']:
                continue

            user_data = response_data['UsersList'][0]
            sam_account_name = user_data.get('SAM_ACCOUNT_NAME')

            if not sam_account_name:
                continue

            # Guardar los campos que nos interesan
            users[sam_account_name] = {
                'FIRST_NAME': user_data.get('FIRST_NAME', ''),
                'LAST_NAME': user_data.get('LAST_NAME', ''),
                'OFFICE': user_data.get('OFFICE', ''),  # Preserva cero inicial
            }

    return users


def _parse_outcome(operation) -> dict:
    """updated_at y resultado desde el POST a ResetPwd y su respuesta.

    El body es repr de Python, no JSON.
    """
    updated_at = None
    status = None
    status_message = None
    status_code = None

    # Buscar POST a ResetPwd para obtener updated_at
    for record in operation:
        if 'HTTP Request: POST' in record['content'] and 'ResetPwd' in record['content']:
            updated_at = record['timestamp']
            break

    if not updated_at:
        raise ValueError("No ResetPwd POST found in operation")

    # Buscar ADM-Raw response para obtener status y statusMessage
    for record in operation:
        if 'ADM-Raw response' in record['content']:
            content = record['content']
            # Extraer el body que es repr de Python: body: [{'key': 'value', ...}]
            body_match = re.search(r'body: (\[.*?\])\s*$', content, re.DOTALL)

            if not body_match:
                continue

            try:
                body_str = body_match.group(1)
                body_list = ast.literal_eval(body_str)
                if body_list and isinstance(body_list, list):
                    response_dict = body_list[0]
                    status = response_dict.get('status')
                    status_message = response_dict.get('statusMessage', '')
                    code_match = re.search(r'\|\s*status:\s*(\d{3})\s*\|', content)
                    status_code = code_match.group(1) if code_match else None
                    break
            except (ValueError, IndexError, KeyError):
                continue

    if status is None:
        raise ValueError("Could not extract status from ADM-Raw response")

    return {
        'updated_at': updated_at,
        'status': status,
        'statusMessage': status_message,
        'status_code': status_code,
    }


def extract_reset(operation) -> ResetRecord:
    """Ensambla las tres etapas en un ResetRecord."""
    # Extraer operation_id del contenido
    operation_id = None
    for record in operation:
        op_id_match = re.search(r'operation_Id=([a-f0-9]{32})', record['content'])
        if op_id_match:
            operation_id = op_id_match.group(1)
            break

    if not operation_id:
        raise ValueError("Could not extract operation_id")

    # Parsear las tres etapas
    request_data = _parse_request(operation)
    users_data = _parse_admanager_users(operation)
    outcome_data = _parse_outcome(operation)

    # Obtener datos del requester y target
    requester = request_data['requester']
    target = request_data['target']

    requester_info = users_data.get(requester, {})
    target_info = users_data.get(target, {})

    # Armar nombres completos
    requester_name = f"{requester_info.get('FIRST_NAME', '')} {requester_info.get('LAST_NAME', '')}".strip()
    target_name = f"{target_info.get('FIRST_NAME', '')} {target_info.get('LAST_NAME', '')}".strip()

    # Armar resultado final (status / statusMessage)
    result = f"{outcome_data['status']} / {outcome_data['statusMessage']}"

    # Crear ResetRecord
    return ResetRecord(
        timestamp=request_data['timestamp'],
        updated_at=outcome_data['updated_at'],
        operation_id=operation_id,
        requester=requester,
        target=target,
        action='resetuser',
        system='ADManager',
        requester_name=requester_name,
        target_name=target_name,
        requester_office=requester_info.get('OFFICE', ''),
        target_office=target_info.get('OFFICE', ''),
        status_code=outcome_data['status_code'],
        result=result,
    )
