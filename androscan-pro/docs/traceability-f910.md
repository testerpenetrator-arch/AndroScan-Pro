# AndroScan — F9.10: Informes

## Estado
Incremento implementado para generación, consulta y descarga de informes PDF, JSON y HTML.

## Alcance y trazabilidad
- **RF-023 / RF-024 (informes):** generación de informe por análisis y descarga en PDF, JSON o HTML.
- **RF-025 (historial):** listado de informes por organización y filtro opcional por análisis.
- **RNF de aislamiento multi-tenant:** toda consulta verifica pertenencia del informe y análisis a la organización solicitada.
- **SEC-logs/auditoría:** creación de informe genera evento `REPORT_CREATED`.
- **CE-006:** exportación en los tres formatos; pruebas de renderizado y comprobación de integridad.
- **F9-D03 / F9-D12:** SQLAlchemy 2.x y migración Alembic `0008_reports`.

## API
- `POST /api/v1/organizations/{organization_id}/reports` — cuerpo: `{"analysis_id":"...","format":"PDF|JSON|HTML"}`.
- `GET /api/v1/organizations/{organization_id}/reports?analysis_id=...` — listado.
- `GET /api/v1/organizations/{organization_id}/reports/{report_id}` — metadatos.
- `GET /api/v1/organizations/{organization_id}/reports/{report_id}/download` — descarga con `Content-Disposition` y `X-Content-SHA256`.

Crear informes requiere rol `ADMIN`, `ANALYST` o `IT_MANAGER`; lectura requiere membresía de la organización. El informe conserva SHA-256 del contenido y trazabilidad del análisis, versión APK, herramientas, hallazgos, evidencia referenciada, revisión humana y descargo de responsabilidad. HTML escapa datos no confiables.

## Límites conocidos
- La generación es síncrona en este incremento; la generación en segundo plano queda como mejora si el volumen lo exige.
- El contenido se almacena en PostgreSQL para el MVP local; la transición a almacenamiento de objetos queda pendiente de decisión de arquitectura/retención.
- No se interpreta la severidad automáticamente ni se sustituye la decisión del analista.

## Pruebas
`backend/tests/test_reporting.py`: formatos JSON/HTML/PDF, escape HTML, trazabilidad y firma PDF. Registrar el resultado real de la suite en el acta de validación del incremento.
