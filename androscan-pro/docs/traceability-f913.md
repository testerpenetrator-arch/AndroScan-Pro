# F9.13 — Actualización del alcance y especificación del cliente Android

## Estado

Especificación documentada tras aprobación del alcance doble (cliente Android instalable + plataforma servidor). No se ha iniciado código Android en este incremento.

## Entregables documentales

- `docs/alcance-cliente-android-f913.md`: arquitectura propuesta, requisitos funcionales y no funcionales, seguridad, criterios de aceptación, decisiones pendientes y límites explícitos.
- Este documento de trazabilidad.

## Decisiones conservadas

- Backend: FastAPI; frontend web: React + TypeScript; PostgreSQL; Redis/Celery; API REST/OpenAPI; Docker; pruebas con pytest.
- El análisis de APK permanece en servidor y sandbox, no en el cliente Android.
- IA externa sigue deshabilitada hasta aprobación específica de privacidad y proveedor.

## Decisión propuesta nueva

- Cliente Android nativo con Kotlin + Jetpack Compose. Requiere aprobación técnica específica antes de iniciar el código móvil.

## Validación de este incremento

- Revisión de consistencia documental y referencias a las API existentes.
- No se declara compilación, pruebas de Android ni APK instalable: el incremento es de especificación.

## Próximo incremento propuesto

F9.14 — Auditoría y observabilidad de la plataforma, incluyendo trazabilidad de peticiones, correlación de logs, métricas y controles de privacidad. La aplicación Android se implementará después de cerrar las decisiones pendientes y aprobar su diseño técnico.
