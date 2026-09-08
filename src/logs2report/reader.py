import re
from pathlib import Path
from typing import TypedDict


class Record(TypedDict):
    """Un registro del log con timestamp, nivel y contenido."""
    timestamp: str
    level: str
    content: str


def read_operations(log_path: str) -> dict[str, list[Record]]:
    """
    Lee un archivo de log y agrupa registros por operation_Id.

    Cada registro puede abarcar varias líneas (incluidas líneas vacías).
    El único delimitador confiable es que una línea empiece con un timestamp ISO.
    Las operaciones pueden estar intercaladas; se agrupan siempre por operation_Id,
    nunca por proximidad.

    Args:
        log_path: Ruta al archivo de log.

    Returns:
        Dict que mapea operation_Id: lista de registros ordenados.
        Cada registro preserva timestamp, nivel y contenido completo
        (incluyendo líneas de continuación).

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    file_path = Path(log_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo de log no encontrado: {log_path}")

    # Regex para detectar inicio de registro (línea con timestamp ISO)
    # Formato: YYYY-MM-DDTHH:MM:SS.FFFFFFZ | LEVEL [operation_Id=...] | ...
    record_start_pattern = re.compile(
        r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s*\|\s*(\w+)\s*\['
    )
    operation_id_pattern = re.compile(r'operation_Id=([a-f0-9]{32})')

    operations: dict[str, list[Record]] = {}
    current_record: Record | None = None
    current_operation_id: str | None = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Eliminar solo el salto de línea final, preservar espacios
            line = line.rstrip('\n\r')

            # Verificar si esta línea empieza un nuevo registro
            record_match = record_start_pattern.match(line)

            if record_match:
                # Guardar registro anterior si existe
                if current_record is not None and current_operation_id is not None:
                    if current_operation_id not in operations:
                        operations[current_operation_id] = []
                    operations[current_operation_id].append(current_record)

                # Iniciar nuevo registro
                timestamp = record_match.group(1)
                level = record_match.group(2)

                # Extraer operation_Id de esta línea
                op_id_match = operation_id_pattern.search(line)
                if op_id_match:
                    current_operation_id = op_id_match.group(1)
                else:
                    # Si no hay operation_Id, usar un ID sintético (no debería ocurrir)
                    current_operation_id = "unknown"

                current_record = {
                    'timestamp': timestamp,
                    'level': level,
                    'content': line
                }
            else:
                # Continuación del registro anterior (línea sin timestamp)
                if current_record is not None:
                    # Agregar línea de continuación con salto de línea
                    current_record['content'] += '\n' + line

    # Guardar último registro
    if current_record is not None and current_operation_id is not None:
        if current_operation_id not in operations:
            operations[current_operation_id] = []
        operations[current_operation_id].append(current_record)

    return operations
