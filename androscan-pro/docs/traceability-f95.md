# AndroScan — F9.5 Sandbox de análisis

## Alcance
F9.5 implementa el perímetro inicial de aislamiento para análisis futuros. No ejecuta APK ni integra todavía MobSF, JADX o Apktool.

## Trazabilidad
| ID | Cobertura |
|---|---|
| RF-010 | Preparación de entorno aislado |
| RF-012 | Fallo controlado de preparación |
| RF-039 | Cancelación compatible con ciclo de análisis |
| RNF-001 | Aislamiento de APK respecto del host |
| RNF-002 | Least privilege |
| RNF-007 | CPU, memoria, procesos, almacenamiento y tiempo |
| RNF-015 | Duración máxima configurable |
| SEC-001 | Escape del sandbox |
| SEC-002 | DoS por APK |
| SEC-003 | Ejecución con privilegios mínimos |
| SEC-010 | Network deny-by-default |
| SEC-014 | Destrucción del entorno temporal |
| DP-014 | Límites de aislamiento: valores iniciales configurables |

## Controles F9.5
- Red del contenedor: `none`.
- Filesystem raíz: `read-only`.
- Capacidades Linux: `ALL` eliminadas.
- `no-new-privileges` habilitado.
- Límite de procesos (`pids-limit`).
- CPU y memoria limitadas.
- `/tmp` y `/work` como `tmpfs` con `nosuid,nodev,noexec`.
- Timeout configurable.
- Identificador del sandbox persistido para trazabilidad.

## Nota de despliegue
El acceso a Docker debe estar restringido al worker dedicado. No se debe montar el socket Docker en el frontend ni exponerlo públicamente. Los valores de hardware y límites definitivos quedan sujetos a DP-014/DP-015.
