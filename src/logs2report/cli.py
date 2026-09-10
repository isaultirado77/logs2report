"""Interfaz de línea de comandos.

    uv run log2report -s data/2026-09-01.log -p reports/2026-09-01.csv
"""

import argparse
from pathlib import Path

from .extract import extract_operation
from .models import ReportRow
from .reader import read_operations
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
    """reader -> extract -> report."""
    rows: list[ReportRow] = []
    for operation_id, operation in read_operations(source).items():
        if operation_id == 'unknown':
            continue
        try:
            row = extract_operation(operation_id, operation)
        except ValueError:
            continue
        if row is not None:
            rows.append(row)
    write_csv(rows, path)


def main() -> None:
    args = build_parser().parse_args()
    run(args.source, args.path)