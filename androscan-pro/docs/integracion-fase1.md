# AndroScan — Etapa 1: integración de la plataforma

**Objetivo:** consolidar el código existente en una única base de proyecto y establecer validaciones repetibles. Esta etapa no equivale a certificar un despliegue productivo.

## Componentes presentes

- API FastAPI con autenticación JWT, organizaciones, aplicaciones y versiones APK, orquestación de análisis, hallazgos, dashboard, comparaciones, informes, asistencia local basada en reglas, administración y health checks.
- Persistencia SQLAlchemy/Alembic y migraciones hasta `0010_admin_configuration`.
- Worker Celery con Redis.
- Almacenamiento compatible con S3 configurado para MinIO en desarrollo.
- Frontend React, TypeScript y Vite.
- Docker Compose de desarrollo y un complemento Compose para ajustes de despliegue.
- Scripts de inicialización/validación de secretos y procedimientos de respaldo/restauración.

## Validación ejecutada para este paquete

- `PYTHONPATH=. pytest -q` desde `backend/`: **44 pruebas aprobadas**.
- `python -m compileall -q backend/app backend/tests`: aprobado.
- `alembic heads`: `0010_admin_configuration (head)`.
- `bash -n` para scripts: aprobado.
- Integridad del ZIP: se verifica después de generarlo.

## Limitaciones de validación

- La instalación de dependencias npm agotó el tiempo disponible en este entorno; por tanto, el build de React/TypeScript **no queda certificado en esta ejecución**.
- Docker Engine no está disponible en el entorno de construcción; no se ejecutó `docker compose up`, ni pruebas end-to-end contra PostgreSQL/Redis/MinIO reales.
- La configuración actual del paquete no incluye todavía el cliente Android nativo ni un APK instalable de AndroScan.
- La integración de MobSF/JADX/Apktool depende de construir y configurar la imagen de herramientas de sandbox correspondiente. No se debe interpretar el éxito de las pruebas unitarias como prueba de análisis real de APK en infraestructura desplegada.
- La asistencia de IA sigue siendo local y basada en reglas; no hay proveedor generativo externo activo.
- Los límites de concurrencia/retención, las alertas/telemetría centralizada, TLS y la recuperación integral siguen requiriendo trabajo de despliegue y pruebas específicas.

## Validación local

Instala las dependencias Python indicadas en `backend/requirements.txt`, y luego ejecuta desde la raíz:

```bash
./scripts/validate-project.sh
```

Para validar también el frontend, instala sus dependencias con `npm install` dentro de `frontend/`; el script ejecutará `npm run build` cuando detecte `frontend/node_modules`.

## Integración continua

`.github/workflows/ci.yml` ejecuta validaciones de backend y compilación del frontend en GitHub Actions cuando el proyecto se sube a un repositorio compatible. El workflow se ha añadido al paquete, pero no se ha ejecutado desde este entorno.


## Corrección de despliegue de almacenamiento (2026-10-16)

El arranque de desarrollo ya no depende de imágenes de MinIO. `STORAGE_BACKEND=local` utiliza el volumen Docker `apk_storage`, montado en `/data/apks` tanto en API como en worker. El adaptador mantiene el modo `STORAGE_BACKEND=s3` para despliegues que proporcionen un servicio S3 compatible. Se añadieron pruebas de almacenamiento local y validación de rutas. Esta corrección se validó con 50 pruebas de backend; no se ejecutó `docker compose up` en el entorno de construcción porque Docker no está instalado aquí.
