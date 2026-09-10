# logs2report

CLI que transforma un archivo `.log` de operaciones en un reporte CSV tabular.

## Descripción

Parsea logs y extrae operaciones de diferentes sistemas (ADManager, SAP), generando un CSV con datos estructurados: timestamps, cuentas, nombres, oficinas y resultado final.

## Operaciones soportadas

- **Reset User (ADManager)**: `users_admin/resetuser`
- **Register User (SAP)**: `sap/register_user`

Cada flujo declara sus propios parámetros y parseo de resultado. El diseño permite agregar nuevas operaciones sin modificar el parser.

## Uso

```bash
uv run logs2report -s data/2026-09-01.log -p reports/2026-09-01.csv
```

- `-s`: Ruta del log de entrada
- `-p`: Ruta del CSV de salida (crea directorios padre si no existen)

## Columnas del reporte

timestamp, updated_at, id, solicitante, target, acción, sistema, nombre_completo_solicitante, nombre_completo_target, oficina_solicitante, oficina_target, status_code, resultado.

Los códigos de oficina conservan el cero inicial (`0520`, no `520`).

## Stack

Python + `uv`. CLI con `argparse`. Parseo con `re` y `json`. Salida con `pandas`. Tests con `pytest`.

## Tests

```bash
uv run pytest
```

47 tests que cubren reader, parser, extracción y generación de reportes contra datos reales.
