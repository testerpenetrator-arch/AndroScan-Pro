# Trazabilidad F9.2 — Identidad y Multi-Tenant

## Alcance

Implementación del primer incremento de identidad y separación de organizaciones.

## Requisitos

| ID | Implementación | Prueba |
|---|---|---|
| RF-001 | `/api/v1/auth/login` + JWT | TST-AUTH-001..005 |
| RF-002 | `organizations` | TST-TEN-001 |
| RF-003 | asociación usuario-organización-rol | TST-TEN-001..003 |
| RF-004 | dependencias de autorización | TST-AUTH-003..005 |
| RNF-006 | autorización por organización | TST-TEN-* |
| RNF-005 | hash de contraseña, configuración de secreto | TST-AUTH-* |
| RNF-008 | eventos de auditoría iniciales | revisión de `audit_events` |

## Roles iniciales

- ADMIN
- ANALYST
- DEVELOPER
- IT_MANAGER

## Decisiones

- JWT para el MVP local.
- Argon2 para hash de contraseñas.
- La organización se determina por el recurso solicitado y la membresía del usuario.
- El frontend no decide autorización; el backend la aplica.

## Limitaciones

El proveedor OIDC/SSO continúa pendiente como decisión de arquitectura futura. Esta implementación local no debe considerarse el diseño definitivo de identidad empresarial.
