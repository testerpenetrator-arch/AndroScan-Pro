# AndroScan — Proyecto acumulado e integración

Este repositorio consolida las entregas anteriores. El trabajo restante se organiza en cuatro etapas generales: (1) integración de plataforma, (2) cliente Android nativo, (3) pruebas integrales y (4) entrega final. Las validaciones internas se agrupan para evitar aprobar cada pequeño incremento.

**Estado verificado de esta entrega:** 44 pruebas de backend aprobadas, sintaxis Python validada y migración Alembic `0010_admin_configuration` como cabeza. El build frontend no se certificó en esta ejecución porque `npm install` agotó el tiempo; Docker no está disponible para una prueba de despliegue integral. El APK instalable Android de AndroScan todavía no está implementado.

Consulta `docs/integracion-fase1.md` para alcance, validación y limitaciones; ejecuta `./scripts/validate-project.sh` para repetir las comprobaciones locales.

---

# AndroScan — Nota de alcance vigente (F9.13)

**Entregable final aprobado:** (1) plataforma servidor de análisis de APK y (2) cliente Android instalable en formato APK. El cliente Android aún no está implementado ni compilado en este paquete; F9.13 actualiza especificaciones y criterios de aceptación. La especificación se encuentra en `docs/alcance-cliente-android-f913.md`. Kotlin + Jetpack Compose es una propuesta pendiente de aprobación técnica específica.

**Distinción importante:** la APK que se carga para analizar es un archivo de entrada no confiable; el APK de AndroScan será la aplicación cliente instalable. El análisis ocurre en el servidor, dentro de entornos aislados.

---

# AndroScan — Paquete acumulado F9.11

Primer incremento de implementación bajo SDD. Este incremento prepara el esqueleto técnico sin integrar todavía autenticación, análisis APK, sandbox ni herramientas de análisis.

## Stack aprobado
- Backend: Python + FastAPI
- DB: PostgreSQL
- ORM/migraciones: SQLAlchemy 2.x + Alembic
- Validación: Pydantic 2.x
- Frontend: React + TypeScript + Vite
- Cola: Redis + Celery
- API: REST + OpenAPI 3.1
- Contenedores: Docker Compose
- Storage: volumen local compartido para desarrollo; backend S3-compatible opcional
- Tests backend: pytest

## Alcance F9.1
- Health checks de API.
- Configuración centralizada mediante variables de entorno.
- Conexión PostgreSQL preparada.
- Sesión SQLAlchemy preparada.
- Cliente Redis/Celery preparado.
- Estructura inicial de frontend.
- Docker Compose para API, frontend, PostgreSQL y Redis; almacenamiento de APK en volumen local compartido.
- Prueba unitaria básica.

No incluye todavía autenticación, multi-tenant, carga de APK, sandbox, herramientas de análisis, IA ni decisiones pendientes posteriores.

## Inicio rápido

El modo predeterminado `STORAGE_BACKEND=local` guarda APK en el volumen Docker `apk_storage`, compartido entre API y worker. No requiere MinIO ni credenciales de un proveedor externo. Para usar un servicio S3 compatible, define `STORAGE_BACKEND=s3` y configura `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` y `S3_BUCKET`.


```bash
docker compose up --build
```

API: http://localhost:8000/docs
Frontend: http://localhost:5173
PostgreSQL: localhost:5432
Redis: localhost:6379

Para desarrollo del backend fuera de Docker, usar Python 3.12+ y ejecutar `pytest` desde `backend/`.

## F9.2 — Identidad y Multi-Tenant

Este incremento agrega autenticación local con JWT, hash de contraseñas mediante Argon2, organizaciones, roles, membresías y autorización por organización. También incorpora auditoría inicial de operaciones de identidad.

### Roles iniciales

- `ADMIN`
- `ANALYST`
- `DEVELOPER`
- `IT_MANAGER`

### Endpoints principales

- `POST /api/v1/auth/login`
- `GET /api/v1/organizations`
- `POST /api/v1/organizations`
- `GET /api/v1/organizations/{organizationId}/users`
- `POST /api/v1/organizations/{organizationId}/users`
- `GET /api/v1/organizations/{organizationId}/users/{userId}/roles`
- `PUT /api/v1/organizations/{organizationId}/users/{userId}/roles`

### Seguridad

La autorización se aplica en backend. El frontend nunca debe considerarse una frontera de seguridad. La separación por organización se valida mediante la tabla `user_organization_roles`.

El proveedor OIDC/SSO empresarial permanece como decisión futura; esta implementación corresponde al MVP local definido en F9.2.

## F9.4 — Orquestación de análisis

La plataforma ya puede registrar y encolar análisis asociados a una versión APK validada. El ciclo de estados y la cancelación están persistidos en PostgreSQL/SQLite de pruebas y el despacho usa Redis + Celery en producción.

> F9.4 no ejecuta APK ni herramientas de análisis. Esa responsabilidad comienza con el sandbox de F9.5 y los runners de herramientas posteriores.

## F9.3 — Aplicaciones y versiones APK

- Registro de aplicaciones por organización.
- Carga y validación estructural de APK.
- SHA-256 y metadatos.
- Almacenamiento S3-compatible.
- Historial de versiones.
- Detección de duplicados.

## F9.5 — Sandbox

Las herramientas se ejecutan únicamente dentro de un contenedor dedicado con red deshabilitada, filesystem raíz de solo lectura, capacidades Linux eliminadas, `no-new-privileges`, límites de CPU/RAM/PIDs y almacenamiento temporal controlado.

## F9.6 — Herramientas de análisis estático

El worker recupera el APK desde almacenamiento S3-compatible, lo copia al sandbox y ejecuta las herramientas habilitadas mediante `docker exec`. Cada ejecución queda registrada en `tool_executions` con herramienta, versión, estado, código de salida, tiempos y salida acotada.

Herramientas integradas en la imagen `androscan/sandbox-tools:0.1`:

- MobSF 4.5.3.
- JADX 1.5.3.
- Apktool 3.0.3.

Un fallo o timeout de una herramienta se registra individualmente y no impide que continúen las demás herramientas.

### Endpoint de trazabilidad de herramientas

`GET /api/v1/organizations/{organization_id}/analyses/{analysis_id}/tools`

### Seguridad

El APK nunca se ejecuta directamente en el host. El worker es el único componente que debe tener acceso al daemon Docker. La imagen de análisis debe ser versionada, escaneada y actualizada mediante cambio controlado.

## F9.9 — Comparación de análisis

Permite comparar dos análisis de la misma aplicación dentro de una misma organización. Los hallazgos se correlacionan por `correlation_key` y se clasifican como `ADDED`, `REMOVED`, `UNCHANGED` o `CHANGED`. La comparación es de solo lectura y no modifica hallazgos ni revisiones originales.

`POST /api/v1/organizations/{organization_id}/comparisons`

Cuerpo: `{"analysis_a_id":"...","analysis_b_id":"..."}`

## F9.10 — Informes PDF, JSON y HTML

Genera informes descargables con datos de la aplicación, versión APK, SHA-256, estado y trazabilidad del análisis, herramientas utilizadas, resumen de hallazgos, severidad, prioridad, evidencia referenciada y estado de revisión humana. Cada artefacto conserva SHA-256 para verificar su integridad. Los informes HTML escapan valores no confiables y todos los formatos incluyen el aviso de que la decisión final de riesgo corresponde al analista.

- `POST /api/v1/organizations/{organization_id}/reports` — genera un informe. Ejemplo: `{"analysis_id":"...","format":"PDF"}`. Formatos: `PDF`, `JSON`, `HTML`.
- `GET /api/v1/organizations/{organization_id}/reports` — lista informes; acepta `analysis_id` opcional.
- `GET /api/v1/organizations/{organization_id}/reports/{report_id}` — metadatos.
- `GET /api/v1/organizations/{organization_id}/reports/{report_id}/download` — descarga del artefacto.

La creación requiere rol `ADMIN`, `ANALYST` o `IT_MANAGER`; la lectura valida la membresía en la organización. La migración `0008_reports` crea el almacenamiento de metadatos y contenido de los informes.

### Validación F9.10

Ejecutar desde `backend/`:

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. pytest -q
```

La suite validada para este paquete pasó **26 pruebas**. La generación PDF usa ReportLab, incluido en `requirements.txt`.

## F9.11 — Asistencia preliminar para revisión de hallazgos

Incorpora una capa inicial de asistencia local que resume los hallazgos seleccionados y propone verificaciones técnicas según la categoría. La respuesta es una guía de apoyo, no una decisión automática de riesgo.

- `POST /api/v1/organizations/{organization_id}/analyses/{analysis_id}/ai-assistance` — genera una sugerencia. Cuerpo opcional: `{"finding_ids":["..."]}`; si se omite la lista, se consideran los hallazgos del análisis.
- `GET /api/v1/organizations/{organization_id}/analyses/{analysis_id}/ai-assistance` — consulta el historial.
- La creación requiere rol `ADMIN`, `ANALYST` o `IT_MANAGER`; la lectura requiere pertenecer a la organización.
- La migración `0009_ai_assistance` persiste la entrada, resultado, autor y descargo de responsabilidad.

**Limitación importante:** el proveedor seleccionado en este incremento es `local-rule-assistant`, basado en reglas deterministas. No hay un modelo generativo conectado ni se envían APK o hallazgos a terceros. La integración de un LLM queda pendiente de aprobar proveedor, ubicación de inferencia, política de datos y controles de coste/privacidad. La asistencia nunca cambia severidad, prioridad ni estado de revisión.

### Validación F9.11

Ejecutar desde `backend/`:

```bash
PYTHONPATH=. pytest -q
```

La suite del paquete F9.11 pasó **30 pruebas** en el entorno de construcción.

## F9.12 — Administración

La API de administración por organización permite consultar y cambiar límites operativos, habilitar herramientas estáticas y revisar eventos de auditoría. Las modificaciones de parámetros quedan registradas en auditoría. Consulte `docs/traceability-f912.md` para conocer qué límites ya se aplican y cuáles quedan como política pendiente de integración.

Endpoints principales:
- `GET/PUT /api/v1/organizations/{organization_id}/admin/settings`
- `GET/PUT /api/v1/organizations/{organization_id}/admin/tools`
- `GET /api/v1/organizations/{organization_id}/admin/audit`

Solo el rol `ADMIN` puede modificar la configuración. `IT_MANAGER` puede consultar configuración y auditoría. La interfaz React incluye controles de administración cuando el usuario tiene permisos suficientes. La construcción de frontend requiere ejecutar `npm install` en el directorio `frontend` antes de `npm run build`.

## F9.14 — Auditoría y observabilidad

- Las respuestas HTTP incluyen `X-Trace-Id` para correlación de incidencias.
- `GET /api/v1/health/live` verifica que la API responde.
- `GET /api/v1/health/ready` verifica la conexión con la base de datos.
- La API registra método, ruta sin parámetros, estado HTTP y duración; no registra cuerpos ni credenciales.
- Consulta `docs/traceability-f914.md` y `docs/operacion-observabilidad-f914.md`.

Validación local de backend: `PYTHONPATH=. pytest -q` desde `backend/`.

## F9.15 — Respaldos y recuperación

Se incorporan `scripts/backup.sh` y `scripts/restore.sh` para PostgreSQL y el volumen de datos de MinIO, además de `docs/recuperacion-respaldos-f915.md` y `docs/traceability-f915.md`. La restauración es destructiva y requiere confirmación literal `RESTORE`. El procedimiento no incluye secretos del `.env`, no cifra ni envía copias fuera del host y no sustituye una prueba de recuperación integral en un entorno de ensayo.

## F9.16 — Endurecimiento de despliegue

Consulta `docs/endurecimiento-despliegue-f916.md`. Para inicializar secretos locales, ejecuta `./scripts/init-secrets.sh` y después `./scripts/validate-env.sh`. Nunca compartas el archivo `.env` ni lo agregues al control de versiones.

## Cliente Android nativo

El código inicial de la aplicación móvil está en `android-client/`. Consulta `android-client/README.md` para herramientas, compilación y limitaciones. La aplicación es un cliente del servidor: el APK seleccionado se envía al backend y no se ejecuta ni analiza localmente.

## Integración y pruebas (15 de octubre de 2026)

La etapa de integración agrega pruebas de contrato de API para el cliente Android, generación/listado de informes desde el cliente y un workflow de calidad en `.github/workflows/quality.yml`. Consulta `docs/etapa3-integracion-pruebas-2026-10-15.md` para las pruebas realizadas y limitaciones. El APK Android aún requiere una compilación confirmada con Android SDK y pruebas de extremo a extremo.

## Preparación de liberación Android

- `scripts/build-android-apk.sh`: valida requisitos y ejecuta `gradle assembleDebug`, mostrando el SHA-256 del artefacto.
- `docs/entrega-final-y-firma-android.md`: pasos de compilación, instalación, firma y checklist de liberación.
- El workflow CI intenta subir el APK debug como artefacto; esto solo se confirma cuando una ejecución real del workflow termina correctamente.
