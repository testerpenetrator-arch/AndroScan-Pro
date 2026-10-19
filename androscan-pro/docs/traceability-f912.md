# F9.12 — Administración de la plataforma

## Alcance
Administración de configuración por organización, catálogo de herramientas estáticas, políticas de habilitación, y consulta de auditoría de administración. Todas las rutas se encuentran bajo `/api/v1/organizations/{organization_id}/admin`.

## Endpoints
- `GET /settings`: consulta parámetros efectivos (ADMIN, IT_MANAGER).
- `PUT /settings`: actualiza parámetros validados (solo ADMIN).
- `GET /tools`: catálogo y herramientas habilitadas (ADMIN, IT_MANAGER).
- `PUT /tools`: actualiza herramientas habilitadas (solo ADMIN).
- `GET /audit?limit=50`: eventos recientes de la organización (ADMIN, IT_MANAGER).

## Parámetros
- `max_apk_size_mb`: 1–500 MB; se aplica al ingreso de APK.
- `max_concurrent_analyses`: 1–50; se guarda para la siguiente integración del planificador de cola; no constituye por sí solo un limitador de concurrencia.
- `analysis_timeout_seconds`: 60–3600; se persiste, pero el sandbox todavía usa el límite global de despliegue hasta que se integre el gestor de límites por análisis.
- `retention_days`: 1–3650; se persiste como política; la eliminación automática programada pertenece a F9.14.
- `ai_assistance_enabled`: activa/desactiva la asistencia local y se valida en el endpoint de creación.
- `external_ai_enabled`: por defecto falso; solo registra la decisión administrativa, no habilita una integración externa.
- `enabled_tools`: subconjunto de `jadx`, `apktool`, `mobsf`; el worker omite herramientas no habilitadas para la organización.

## Seguridad
- Aislamiento de configuración por organización.
- Solo ADMIN puede modificar parámetros y política de herramientas.
- ADMIN/IT_MANAGER pueden consultar configuración y auditoría.
- Validación de rangos y nombres de herramienta; auditoría de cambios.
- No se permite habilitar IA externa cuando la asistencia IA está deshabilitada.

## Trazabilidad
- RF-001/RF-002: roles y administración.
- RF-030/RF-031: configuración y auditoría.
- RNF-001/RNF-002: autorización y aislamiento de organizaciones.
- SEC-003/SEC-004: mínimo privilegio y aislamiento por tenant.

## Limitaciones abiertas
1. El límite de análisis simultáneos aún no es impuesto por un semáforo distribuido; requiere integración con Redis/Celery.
2. El tiempo de sandbox sigue usando el límite global del servidor; falta aplicarlo dinámicamente al crear el contenedor.
3. La retención se configura pero el borrado automático se implementa en F9.14.
4. `external_ai_enabled` no conecta proveedor externo; se mantiene sin efecto hasta una fase explícita de integración y aprobación de privacidad.
5. El panel React aún no incluye una pantalla administrativa completa; esta fase expone la API y deja su UI para la integración de frontend.
