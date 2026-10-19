# F9.11 — Asistencia preliminar para revisión de hallazgos

## Alcance
- `RF-022`, `RF-023`, `RF-024`: asistencia explicativa, resumen y supervisión humana.
- `RNF-001`, `RNF-002`, `RNF-010`, `RNF-011`: acceso autenticado, separación por organización, auditoría y protección de datos.
- `SEC-010`, `SEC-011`, `SEC-012`: tratamiento de entradas como datos no confiables, minimización y prohibición de ejecución de acciones por el asistente.

## Implementación
- Persistencia `AIAssistance` y migración `0009_ai_assistance`.
- `POST /api/v1/organizations/{organization_id}/analyses/{analysis_id}/ai-assistance` crea una sugerencia para todos los hallazgos o para una selección explícita.
- `GET` en la misma ruta devuelve el historial de sugerencias de esa organización y análisis.
- La versión F9.11 usa reglas locales deterministas (`local-rule-assistant`). No se conecta a un proveedor generativo externo porque la decisión de proveedor y la autorización de salida de datos siguen pendientes.
- Se almacenan los hallazgos de entrada, resultado estructurado, autor, fecha y descargo de responsabilidad. Se genera evento de auditoría.

## Límites de seguridad
- No se transmite el APK ni la evidencia a servicios externos.
- No se alteran los campos de severidad, prioridad, revisión ni notas de analista.
- La respuesta indica que se requiere revisión humana y que no confirma explotabilidad.
- Acceso de creación: `ADMIN`, `ANALYST`, `IT_MANAGER`; lectura limitada a miembros de la organización.

## Decisiones pendientes
- `DP-014-AI`: proveedor/modelo generativo y ubicación de inferencia.
- `DP-015-AI`: campos permitidos para contexto, consentimiento y política de salida externa.
- Definir límites de tokens, timeout, coste, redacción de secretos y evaluación de calidad antes de habilitar un LLM.

## Criterios de aceptación
- AIA-001: solo se procesan hallazgos pertenecientes al análisis y organización indicada.
- AIA-002: la respuesta siempre incluye advertencia de revisión humana.
- AIA-003: no se modifica la severidad, prioridad o estado original de los hallazgos.
- AIA-004: las solicitudes se auditan y quedan consultables por miembros de la organización.
