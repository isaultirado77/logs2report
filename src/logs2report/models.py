from dataclasses import dataclass


@dataclass
class ReportRow:
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
    status_code: str
    result: str


COLUMNS: list[tuple[str, str]] = [
    ("timestamp", "timestamp"),
    ("updated_at", "updated_at"),
    ("id", "operation_id"),
    ("solicitante", "requester"),
    ("target", "target"),
    ("acción", "action"),
    ("sistema", "system"),
    ("nombre_completo_solicitante", "requester_name"),
    ("nombre_completo_target", "target_name"),
    ("oficina_solicitante", "requester_office"),
    ("oficina_target", "target_office"),
    ("status_code", "status_code"),
    ("resultado", "result"),
]