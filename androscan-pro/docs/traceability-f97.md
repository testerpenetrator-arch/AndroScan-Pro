# F9.7 — Trazabilidad: normalización y gestión de hallazgos

| ID | Implementación | Trazabilidad | Validación |
|---|---|---|---|
| F97-001 | Modelo `Finding` | F3: Hallazgo, categoría, severidad, prioridad | Test de persistencia |
| F97-002 | `tool_execution_id`, `rule_id`, `raw_result_ref` | F3/F6: procedencia completa | Test de provenance |
| F97-003 | `correlation_key` reutilizable | F3: correlación sin pérdida de procedencia | Múltiples hallazgos pueden compartir clave |
| F97-004 | Categorías MASVS: STORAGE/CRYPTO/AUTH/NETWORK/PLATFORM/CODE/RESILIENCE/PRIVACY/OTHER | F6: mapeo MASVS | Validadores Pydantic |
| F97-005 | Severidad INFO/LOW/MEDIUM/HIGH/CRITICAL | F1/F6 | Validadores Pydantic |
| F97-006 | Prioridad P4/P3/P2/P1 independiente de severidad | F1/F2/F6 | Validadores Pydantic |
| F97-007 | `FindingReview` y estados PENDING/CONFIRMED/DISMISSED | F1/F3: revisión humana | Test de persistencia |
| F97-008 | Justificación y notas del analista | F1/F6: decisión humana trazable | Test de persistencia |
| F97-009 | API de consulta/creación/revisión | F5/F8 | Suite API + autorización existente |
| F97-010 | Migración Alembic `0007_findings` | F9-D03/F9-D12 | `alembic upgrade head` validado en SQLite |

## Regla de decisión
La plataforma no convierte automáticamente severidad en decisión final. La severidad representa impacto técnico y la prioridad representa atención requerida; la confirmación o descarte pertenece al analista autorizado.

## Fuera de F9.7
La asistencia de IA, recomendaciones automáticas de remediación, correlación avanzada entre herramientas y modificación automática de decisiones quedan fuera de este incremento y se implementarán en sus fases/incrementos aprobados.
