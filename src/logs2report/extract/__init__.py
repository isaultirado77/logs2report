"""Extracción de filas del reporte a partir de operaciones del log.

Cada flujo vive en su propio módulo y se declara como un Flow.
Para agregar uno nuevo: crear su módulo y sumarlo a FLOWS.
"""

from ..models import ReportRow
from ..reader import Operation
from .common import build_row
from .register import REGISTER
from .reset import RESET

__all__ = ["FLOWS", "extract_operation"]

# Se prueban en orden; gana el primero que aplica.
FLOWS = (RESET, REGISTER)


def extract_operation(operation_id: str, operation: Operation) -> ReportRow | None:
    """Fila del reporte, o None si la operación no pertenece a ningún flujo.

    Raises:
        ValueError: si pertenece a un flujo pero le faltan datos.
    """
    for flow in FLOWS:
        if flow.applies_to(operation):
            return build_row(flow, operation_id, operation)
    return None
