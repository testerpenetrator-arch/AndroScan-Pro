# F9.8 — Dashboard y consulta operativa

## Objetivo
Implementar la primera consola React de AndroScan para consultar el estado de la organización autenticada sin introducir nuevas decisiones de riesgo.

## Trazabilidad
- RF-029: dashboard restringido al alcance autorizado.
- RF-030: aplicación/versión/historial visible.
- RF-032: estado actualizado de análisis visible.
- RF-021/022: categoría, severidad y prioridad visibles separadamente.
- RNF-006: consultas siempre filtradas por organización.
- RNF-011: endpoint de dashboard diseñado para respuesta agregada.
- RNF-028/029: errores conservan contexto HTTP; no se muestran secretos.
- SEC-006: aislamiento por organización aplicado mediante dependencia de autorización.

## No incluido
- Edición de hallazgos.
- Decisiones automáticas de riesgo.
- IA.
- Comparación de versiones.
- Generación de reportes.

## Cierre F9.8
- Se agregan tipificaciones `@types/react` y `@types/react-dom` requeridas por TypeScript.
- Se documenta el procedimiento de instalación/build en `frontend/BUILD.md`.
- No se introducen funciones de comparación, reportes o IA en este cierre.
