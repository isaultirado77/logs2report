# Formato del log y mapeo de columnas

Referencia para escribir y mantener el parser. Los ejemplos de logs se incluyen en `data/`.

## Formato de línea

```
<timestamp ISO Z> | <NIVEL> [operation_Id=<hex32>] | <contenido>
```

Ejemplo:

```
2026-09-01T00:02:39.862105Z | INFO [operation_Id=b5ab6865ca8ac9629ff2eb303637d408] | HTTP Request: ...
```

**Los registros son multilínea.** El contenido de un registro puede continuar en las
líneas siguientes, incluidas líneas vacías, hasta que aparece otra línea que empieza
con un timestamp ISO. El inicio de registro es el único delimitador confiable.

## Estructura de una operación de reseteo

Un reseteo completo son cuatro etapas que comparten el mismo `operation_Id`. Las
operaciones pueden aparecer intercaladas entre sí, por lo que la agrupación se hace
siempre por ese id.

### 1. Entrada - solicitud de reseteo

```
HTTP Request: http://apitools.com:8000/v3/users_admin/resetuser?sAMAccountName_requester=admsistemas520&sAMAccountName_target=520000228 "HTTP/1.1" 200
```

Marca el inicio de la operación. De aquí salen el timestamp, el requester y el target.
La presencia de `users_admin/resetuser` es lo que identifica la operación como
reseteo; es el filtro de entrada del MVP.

### 2. Consultas a ADManager - datos de los usuarios

Por cada operación hay **dos** consultas `SearchUser`, una por cuenta. Cada una son
dos registros: la línea `HTTP Request: GET .../SearchUser?...` y, a continuación, un
registro `ADManagerRawClient.get_users_list_info_from_admanager invoked` que contiene
el JSON crudo de la respuesta.

**El orden de las dos consultas no es estable.** En unas operaciones se consulta
primero el target y en otras primero el requester. La cuenta a la que corresponde
cada respuesta se identifica por el parámetro `filter`, que viene URL-encoded:

```
filter=%28sAMAccountName%3Aequal%3A520000228%29
```

decodifica a `(sAMAccountName:equal:520000228)`. Alternativamente puede leerse
`SAM_ACCOUNT_NAME` dentro del propio JSON de respuesta, que es más directo.

La respuesta es **JSON válido** (comillas dobles) embebido en el texto del registro,
después de `Raw Response: `. Campos que nos interesan:

| Campo | Uso |
|---|---|
| `SAM_ACCOUNT_NAME` | identificar a quién corresponde el registro |
| `FIRST_NAME` | nombre |
| `LAST_NAME` | apellidos |
| `OFFICE` | oficina - **conserva cero inicial** (`0520`), tratar como texto |

### 3. Consulta a Proactivanet

```
ProactivanetRawClient, method = GET, url = Users, proactivanet_raw_response: [{'Id': 'ANON_...', ...}]
```

Solo se consulta el **requester**. El payload no es JSON: es el `repr` de una lista de
dicts de Python (comillas simples, `None`, `False`), así que no se puede parsear con
el mismo mecanismo que ADManager.

**El MVP no usa esta etapa.** Todos sus campos vienen anonimizados (`ANON_...`), así
que no aportan ninguna columna del reporte. Se documenta para saber que existe y
poder ignorarla sin dudar.

### 4. Ejecución del reseteo - desenlace

Dos registros consecutivos. Primero el POST:

```
HTTP Request: POST https://admanager.retailstore.com/RestAPI/ResetPwd?...&inputFormat=%5B%7B%22userPrincipalName%22%3A%22520000228%40retailstore.com%22%7D%5D "HTTP/1.1 200 "
```

Su timestamp es el `updated_at`. Luego la respuesta:

```
ADM-Raw response | status: 200 | body: [{'sAMAccountName': '520000228', ..., 'reset': 'yes', 'statusMessage': 'Password reset successful.', 'status': '1'}]
```

También en formato `repr` de Python, no JSON. Campos relevantes: `status` (`'1'` =
éxito), `statusMessage`, `reset`.

## Mapeo de columnas

| Columna | Origen |
|---|---|
| Requisitos | - sin definir, se emite vacía |
| timestamp | timestamp de la línea de entrada (etapa 1) |
| updated_at | timestamp del POST a `ResetPwd` (etapa 4) |
| id | `operation_Id` |
| solicitante | `sAMAccountName_requester` de la etapa 1 |
| target | `sAMAccountName_target` de la etapa 1 |
| acción | derivada del endpoint; en el MVP constante para `resetuser` |
| sistema | derivada del host de la etapa 4 (`admanager...` → ADManager) |
| nombre completo solicitante | `FIRST_NAME` + `LAST_NAME` del SearchUser del requester |
| nombre completo target | `FIRST_NAME` + `LAST_NAME` del SearchUser del target |
| oficina solicitante | `OFFICE` del SearchUser del requester |
| oficina target | `OFFICE` del SearchUser del target |
| resultado final | `status` / `statusMessage` de la etapa 4 |

## Valores redactados

`[REDACTED_TOKEN]` y `[REDACTED_PASSWORD]` aparecen en las URLs y payloads. Son
literales del log anonimizado, no un error de parseo. Ninguno se usa.

## Casos no cubiertos por el MVP

Documentados aquí para el módulo de preprocesamiento futuro, **no** para implementarse
ahora:

- Operaciones incompletas: el archivo puede cortarse a media operación, o el POST
  final puede no existir (fallo, timeout).
- `SearchUser` sin resultados (`count: 0`), que dejaría nombres y oficina vacíos.
- Reseteos con resultado de error (`status` distinto de `'1'`).
- Campos con valores centinela: `<not set>` y `-` aparecen en `EMPLOYEE_ID`,
  `EXTENSIONATTRIBUTE3` e `INITIAL`.