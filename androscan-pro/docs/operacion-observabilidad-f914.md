# Guía operativa de observabilidad F9.14

## Verificación rápida
- `GET /api/v1/health/live`: confirma que el proceso responde.
- `GET /api/v1/health/ready`: confirma que el proceso puede consultar la base de datos.
- Copiar el valor de `X-Trace-Id` de una respuesta para buscar el evento correspondiente en los logs.

## Logs
La aplicación usa `logging` estándar. En contenedores, los logs se envían a stdout/stderr y pueden recogerse con el sistema de logging del host o del orquestador.

## Seguridad
No activar logging de cuerpos HTTP ni cabeceras de autorización en producción. Restringir el acceso a logs, definir rotación y retención y sincronizar la hora del servidor. No registrar APK, contraseñas, JWT ni secretos.

## Estado de integración
Los endpoints de salud y la correlación de peticiones están implementados en esta fase. La exportación a una plataforma centralizada, las métricas y las alertas permanecen como trabajo posterior.
