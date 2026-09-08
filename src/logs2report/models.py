from dataclasses import dataclass


@dataclass
class ResetRecord:
    """Una operación de reseteo, ya extraída y lista para el reporte."""

    timestamp: str
    updated_at: str | None
    operation_id: str
    requester: str
    target: str
    action: str
    system: str
    requester_name: str
    target_name: str
    requester_office: str
    target_office: str
    result: str
    requisitos: str = ""  # sin definir, vacia


# Orden de las columnas del CSV.
# tuplas (encabezado en el CSV, atributo de ResetRecord).
COLUMNS: list[tuple[str, str]] = [
    ("Requisitos", "requisitos"),
    ("timestamp", "timestamp"),
    ("updated_at", "updated_at"),
    ("id", "operation_id"),
    ("solicitante", "requester"),
    ("target", "target"),
    ("acción", "action"),
    ("sistema", "system"),
    ("nombre completo solicitante", "requester_name"),
    ("nombre completo target", "target_name"),
    ("oficina solicitante", "requester_office"),
    ("oficina target", "target_office"),
    ("resultado", "result"),
]