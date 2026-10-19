# F9.14 — Auditoría y observabilidad

## Objetivo
Mejorar el diagnóstico operativo y la correlación de peticiones sin registrar secretos ni contenido de APK.

## Cambios incluidos
- Middleware HTTP que acepta un `X-Trace-Id` de formato seguro o genera un UUID.
- Devolución de `X-Trace-Id` en las respuestas para correlacionar incidencias.
- Registro estructurado de método, ruta sin query string, código HTTP y duración.
- Registro de excepciones con identificador de trazabilidad, sin registrar cabeceras, tokens ni cuerpos.
- Endpoint de liveness: `GET /api/v1/health/live`.
- Endpoint de readiness: `GET /api/v1/health/ready`, que verifica conectividad con la base de datos y responde 503 si no está disponible.
- Pruebas de trazabilidad, saneamiento del identificador y comprobaciones de salud.

## Criterios de aceptación
- OBS-001: toda respuesta HTTP incluye `X-Trace-Id`.
- OBS-002: los identificadores entrantes con caracteres no permitidos se sustituyen por un UUID.
- OBS-003: los logs HTTP incluyen ruta, método, estado, duración y trace ID.
- OBS-004: los logs no incluyen query strings, tokens ni cuerpo de la petición.
- OBS-005: liveness no depende de la base de datos.
- OBS-006: readiness verifica la base de datos y devuelve 503 cuando falla.

## Limitaciones conocidas
- Los logs se emiten mediante el sistema de logging estándar de Python; la agregación centralizada (por ejemplo, Loki/ELK), métricas Prometheus, alertas y trazas distribuidas aún requieren configuración de despliegue.
- El registro de auditoría de negocio sigue separado de los logs técnicos.
- La retención y protección del almacenamiento de logs debe configurarse en el entorno de despliegue.

## Trazabilidad
- Fase 5: `X-Trace-Id` y errores estructurados de API.
- Fase 6: no registrar secretos ni datos sensibles.
- Fase 7: pruebas de observabilidad y regresión.
- Fase 8: incremento de auditoría/observabilidad.
