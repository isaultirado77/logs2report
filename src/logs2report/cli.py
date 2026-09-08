"""Interfaz de línea de comandos.

    uv run log2report -s data/2026-09-01.log -p reports/2026-09-01.csv
"""

import argparse
from pathlib import Path
from .reader import read_operations
from .extract import is_reset_operation, extract_reset
from .report import write_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="log2report",
        description="Transforma un log de operaciones en un reporte CSV.",
    )
    parser.add_argument("-s", "--source", type=Path, required=True, help="log de entrada")
    parser.add_argument("-p", "--path", type=Path, required=True, help="CSV de salida")
    return parser


def run(source: Path, path: Path) -> None:
    """reader -> filtro de reseteos -> extract -> report."""
    # Leer log y agrupar por operation_id
    operations = read_operations(str(source))

    # Filtrar operaciones de reseteo y extraer
    reset_records = []
    for operation_id, records in operations.items():
        if is_reset_operation(records):
            try:
                record = extract_reset(records)
                reset_records.append(record)
            except (ValueError, KeyError) as e:
                # Ignorar operaciones que no se pueden extraer completamente
                continue

    # Guardar CSV
    write_csv(reset_records, str(path))


def main() -> None:
    args = build_parser().parse_args()
    run(args.source, args.path)
