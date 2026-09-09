# logs2report

CLI que transforma un archivo `.log` de operaciones en un reporte CSV tabular.

```bash
uv run log2report -s data/2026-09-01.log -p reports/2026-09-01.csv
```

`-s` ruta del log de entrada, `-p` ruta del CSV de salida. Reejecutable para cualquier fecha.

## Stack

Python + `uv`. CLI con `argparse` (stdlib). Parseo con `re`, salida con `pandas`. Tests con `pytest`.

## Estructura

```
src/logs2report/   # código de la app
data/              # logs de muestra (anonimizados, read-only)
docs/logs-format.md # anatomía del log y mapeo de columnas
tests/
nbs/               # exploración; no es parte del paquete
```

## Alcance actual (MVP)

Solo se procesan las operaciones de reseteo de usuarios de ADManager, identificadas
por el endpoint `users_admin/resetuser`. El diseño debe permitir agregar otras
acciones después sin reescribir el parser.

No implementar todavía: validación robusta, manejo de operaciones incompletas,
reintentos, logging estructurado. Eso va en un módulo de preprocesamiento futuro.

## Columnas del reporte

`Requisitos`, `timestamp`, `updated_at`, `id`, `solicitante`, `target`, `acción`,
`sistema`, nombre completo de solicitante y de target, oficina de solicitante y de
target, `resultado final`.

El origen de cada columna está en `docs/logs-format.md`. Consultar ese archivo antes
de tocar el parser.

`Requisitos` se emite vacía: nadie ha confirmado aún qué contiene.

## Convenciones

- La unidad de parseo es la **operación** (agrupada por `operation_Id`), no la línea.
  Los registros son multilínea.
- `OFFICE` conserva el cero inicial (`0520`); tratar siempre como texto.
- Los timestamps se escriben tal cual vienen en el log (UTC), sin conversión.
- No procesar `data/` con rutas hardcodeadas: todo entra por los argumentos de la CLI.

## Antes de dar algo por terminado

`uv run pytest` y una corrida real contra un log de `data/`.