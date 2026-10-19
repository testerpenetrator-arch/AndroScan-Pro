# AndroScan — F9.3 Aplicaciones y versiones APK

## Alcance implementado

F9.3 implementa el ciclo de registro de aplicación, carga controlada de APK, validación estructural, SHA-256, metadatos y almacenamiento S3-compatible. No ejecuta APK ni integra MobSF, JADX o Apktool.

## Trazabilidad

| Requisito | Implementación | Prueba |
|---|---|---|
| RF-005 | `POST /organizations/{organization_id}/applications/{application_id}/apk` y asociación a organización/aplicación/usuario | `test_create_application_and_list_versions` |
| RF-006 | extensión, firma ZIP, límite configurable, ZIP íntegro y estructura mínima | `test_invalid_apk_is_rejected` |
| RF-007 | SHA-256 y metadatos estructurales | `test_create_application_and_list_versions` |
| RF-008 | rechazo antes de crear versión/almacenamiento lógico cuando falla validación | `test_invalid_apk_is_rejected` |
| RF-030 | historial de `APKVersion` por `Application` | `test_create_application_and_list_versions` |
| RNF-012 | validación hasta el límite operativo configurable de 100 MB, sujeto a DP-009 | cobertura de validación; medición de rendimiento pendiente F9.16 |
| RNF-042 | solo `.apk` y contenedor APK/ZIP con estructuras requeridas | `test_invalid_apk_is_rejected` |
| RNF-045 | `MAX_APK_SIZE_MB` configurable sin modificar código | configuración `max_apk_size_mb` |
| SEC-006/SEC-007 | validación de entrada y protección básica frente a rutas peligrosas del ZIP | `apk_validation.py` |

## Decisiones conservadas

- SHA-256 identifica el contenido del APK.
- La separación por organización sigue siendo obligatoria aunque el hash coincida.
- El almacenamiento es S3-compatible mediante MinIO en el entorno local.
- El límite de 100 MB es operativo/provisional y no cierra DP-009.
- La carga no dispara análisis todavía.
