# F9.9 — Comparación de análisis y versiones

## Alcance
- Comparar dos análisis pertenecientes a la misma organización y aplicación.
- Clasificar hallazgos como `ADDED`, `REMOVED`, `UNCHANGED` o `CHANGED`.
- Emparejar por `correlation_key`; los duplicados se emparejan uno a uno para no ocultar procedencia.
- Comparar título, descripción, categoría, severidad y prioridad. El estado de revisión se muestra como contexto, pero no determina el delta.
- La operación es de solo lectura: no cambia hallazgos, evidencias ni revisiones originales.

## Endpoint
`POST /api/v1/organizations/{organization_id}/comparisons`

```json
{"analysis_a_id":"<id>" , "analysis_b_id":"<id>"}
```

## Seguridad
- Requiere autenticación y pertenencia a la organización.
- Los análisis deben pertenecer a la organización solicitada.
- Ambos análisis deben corresponder a la misma aplicación.
- No se permite comparar un análisis consigo mismo.

## Limitaciones
La calidad del emparejamiento depende de que las herramientas generen `correlation_key` estables. Esta fase no crea reportes exportables; corresponde a F9.10.
