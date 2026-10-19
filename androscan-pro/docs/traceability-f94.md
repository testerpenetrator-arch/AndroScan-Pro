# AndroScan — F9.4 Orquestación de análisis

## Alcance

Este incremento implementa la creación, encolado, consulta, listado y cancelación controlada de análisis. No ejecuta APK ni herramientas de análisis.

## Trazabilidad

| ID | Cobertura |
|---|---|
| RF-009 | Registro de análisis, identificador, versión y estado |
| RF-011 | Encolado y gestión inicial del estado |
| RF-016 | Estructura para estado final/resumen, sin completar ejecución real |
| RF-029 | Consulta restringida a organización |
| RF-030 | Historial de análisis por aplicación |
| RF-039 | Cancelación controlada |
| RNF-017 | Desacoplamiento mediante Celery/Redis |
| RNF-023 | Persistencia de análisis en BD |
| RNF-024 | Base para estados y futuros reintentos controlados |
| RNF-028 | Integrable con observabilidad estructurada |
| RNF-029 | trace_id persistido |
| SEC-006 | Aislamiento de tenant en consultas |

## Estados

`CREATED → QUEUED → PREPARING → RUNNING → PROCESSING_RESULTS → COMPLETED`

Desde estados activos se contempla `CANCELLED` y `FAILED` según la transición permitida.

En F9.4 el worker solo llega hasta `PREPARING`; la ejecución real continúa en F9.5/F9.6.

## Restricción explícita

No se ejecuta código del APK, no se descomprime el APK en el worker y no se invoca MobSF, JADX, Apktool, Frida ni otros analizadores.
