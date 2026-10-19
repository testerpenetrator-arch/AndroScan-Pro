# AndroScan — Trazabilidad F9.6

## Objetivo
Integrar herramientas de análisis estático dentro del sandbox y conservar la procedencia de cada ejecución.

| ID | Implementación |
|---|---|
| RF-013 | Registro y ejecución de herramientas habilitadas |
| RF-014 | `ToolExecution` conserva herramienta, versión, estado, código y salida |
| RF-015 | Un fallo/timeout de una herramienta se registra y permite continuar |
| RNF-027 | Fallo individual no corrompe el análisis global |
| RNF-043 | Versiones de herramientas registradas |
| SEC-001 | Ejecución exclusivamente mediante `docker exec` en sandbox |
| SEC-002 | Herramientas sin privilegios y dentro de límites F9.5 |
| SEC-003 | Red del sandbox bloqueada |
| SEC-013 | Herramientas tratadas como dependencias potencialmente vulnerables |

## Herramientas
- MobSF 4.5.3, imagen oficial fijada.
- JADX 1.5.3, integrado en la imagen de análisis.
- Apktool 3.0.3, integrado en la imagen de análisis.

Las versiones deben actualizarse mediante cambio controlado y pruebas de regresión.
