# logs2report

CLI que transforma un archivo `.log` de operaciones en un reporte CSV tabular.

## Descripción

Parsea logs de ADManager y extrae operaciones de reseteo de usuarios, generando un CSV con datos estructurados: timestamps, cuentas, nombres, oficinas y resultado final.

## MVP: Operaciones de reset user

Este MVP procesa únicamente operaciones de reseteo de usuarios (`users_admin/resetuser`). El diseño permite agregar otras acciones sin reescribir el parser.

Cada operación consta de 4 etapas:
1. Solicitud de reseteo (HTTP POST)
2. Consultas a ADManager por datos de requester y target
3. Consulta a Proactivanet (no usada en MVP)
4. Ejecución y resultado del reseteo

## Uso

```bash
uv run log2report -s data/2026-09-01.log -p reports/2026-09-01.csv
```

- `-s`: Ruta del log de entrada
- `-p`: Ruta del CSV de salida (crea directorios padre si no existen)

## Columnas del reporte

Requisitos, timestamp, updated_at, id, solicitante, target, acción, sistema, nombre completo solicitante, nombre completo target, oficina solicitante, oficina target, resultado.

Los códigos de oficina conservan el cero inicial (`0520`, no `520`).

## Stack

Python + `uv`. CLI con `argparse`. Parseo con `re` y `json`. Salida con `pandas`. Tests con `pytest`.

## Tests

```bash
uv run pytest
```

47 tests que cubren reader, parser, extracción y generación de reportes contra datos reales.
