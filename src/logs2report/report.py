from pathlib import Path
import pandas as pd
from .models import ResetRecord, COLUMNS


def to_dataframe(records: list[ResetRecord]) -> pd.DataFrame:
    """Construye DataFrame desde lista de ResetRecord.

    Usa COLUMNS de models.py como única fuente de orden y encabezados.
    Todos los valores son str para preservar formatos (e.g., OFFICE con cero).
    """
    data = []
    for record in records:
        row = {}
        for csv_header, attr_name in COLUMNS:
            value = getattr(record, attr_name, '')
            row[csv_header] = str(value) if value is not None else ''
        data.append(row)

    # Crear DataFrame con las columnas en el orden de COLUMNS
    column_headers = [header for header, _ in COLUMNS]
    df = pd.DataFrame(data, columns=column_headers)

    return df


def write_csv(records: list[ResetRecord], output_path: str) -> None:
    """Escribe los registros en un CSV.

    Crea los directorios padre si no existen.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df = to_dataframe(records)
    df.to_csv(output_path, index=False)
