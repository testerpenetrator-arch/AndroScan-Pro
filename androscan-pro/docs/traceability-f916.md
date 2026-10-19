# Trazabilidad F9.16 — Endurecimiento y secretos

| Requisito | Implementación | Verificación |
|---|---|---|
| F916-01 No conservar credenciales de desarrollo en Compose | Variables obligatorias para contraseña PostgreSQL y credenciales MinIO | Inspección de `docker-compose.yml` |
| F916-02 Generar secretos únicos | `scripts/init-secrets.sh` con `openssl rand -hex` y `umask 077` | Ejecución en directorio temporal; comprueba permisos y valores no vacíos |
| F916-03 No sobrescribir secretos existentes | Inicializador falla si `.env` ya existe | Prueba de segunda ejecución |
| F916-04 Validar secretos | `scripts/validate-env.sh` | Casos válido e inválido en entorno temporal |
| F916-05 Rechazar valores inseguros en producción | `backend/app/core/security_config.py`, validado en lifespan | Pruebas unitarias de secreto corto, predeterminado y válido |
| F916-06 Reducir exposición de puertos | Bind a localhost para API, MinIO y Vite | Inspección de Compose |
| F916-07 Reducir privilegios API | Usuario no root, `cap_drop: ALL`, `no-new-privileges`, rootfs de solo lectura | Inspección de Dockerfile/Compose; falta ejecución Docker real |
| F916-08 Documentar límites | `docs/endurecimiento-despliegue-f916.md` | Revisión documental |

## Resultado

`PYTHONPATH=. pytest -q`: 44 passed. La validación sintáctica de los scripts Bash se ejecutó por separado. No se ejecutó Docker Compose ni una prueba integral de producción, por lo que los controles de contenedor quedan pendientes de validación en un host de ensayo.
