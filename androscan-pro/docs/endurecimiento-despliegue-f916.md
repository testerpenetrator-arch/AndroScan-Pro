# F9.16 — Endurecimiento del despliegue y gestión de secretos

## Objetivo

Reducir el riesgo de desplegar AndroScan con contraseñas predeterminadas, publicar puertos de administración innecesariamente o ejecutar la API con privilegios excesivos. Esta fase es una base de endurecimiento, no una certificación de producción.

## Inicialización

1. Instalar Docker Engine/Compose y OpenSSL en el host.
2. Ejecutar `./scripts/init-secrets.sh`. El script se niega a sobrescribir un `.env` existente y crea el archivo con permisos `0600`.
3. Ejecutar `./scripts/validate-env.sh`.
4. Revisar cuidadosamente `.env`; no enviarlo por correo, no subirlo al repositorio y no incluirlo en paquetes o respaldos sin cifrado.
5. Iniciar el entorno de desarrollo con `docker compose up --build`.
6. Para la configuración complementaria de producción: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d`. Antes de exponer servicios a Internet, desplegar un proxy inverso con TLS, firewall, control de acceso y procedimientos de actualización.

## Controles añadidos

- Eliminación de credenciales literales predeterminadas del Compose.
- Generación de secretos aleatorios con OpenSSL; archivo `.env` protegido con permisos `0600`.
- Validador básico de variables sensibles.
- Validación en el arranque de la API cuando `APP_ENV=production`: rechaza secreto JWT vacío, corto o predeterminado y secreto S3 predeterminado.
- Puertos de API, MinIO y Vite enlazados a `127.0.0.1` por defecto para evitar publicación directa en interfaces externas.
- API con `no-new-privileges`, eliminación de capabilities y sistema de archivos raíz de solo lectura; `/tmp` temporal, sin ejecución.
- Imagen de API ejecutada como usuario sin privilegios.
- `.env`, respaldos y dumps excluidos de Git.

## Limitaciones conocidas / antes de producción

- El entorno aún usa imágenes etiquetadas de forma no inmutable; fijar digest y establecer proceso de actualización de seguridad.
- Redis no tiene autenticación/TLS configurada; mantenerlo en red privada y endurecer antes de entornos multiusuario expuestos.
- No se incluye gestor de secretos externo (Vault, SOPS u otro), rotación automatizada ni cifrado automático de respaldos.
- El archivo Compose de producción no configura por sí solo proxy inverso, TLS, firewall, WAF ni política de copias remotas.
- El servicio de análisis/sandbox requiere revisión específica de permisos y aislamiento en el host real; no se debe exponer Docker socket a cargas no confiables.
- La UI Vite es solo desarrollo; el perfil `development` evita iniciarla con el complemento de producción. El despliegue de frontend estático debe resolverse por separado.
- La configuración de producción debe usar secretos largos y únicos. No reutilizar la contraseña de la base de datos como credencial administrativa personal.

## Pruebas realizadas

- Suite backend: `PYTHONPATH=. pytest -q` — 44 pruebas aprobadas.
- `bash -n` para scripts de inicialización/validación — aprobado.
- Pruebas aisladas de inicialización y validación de secretos — registradas en trazabilidad.

No se afirma haber ejecutado un despliegue real con Docker ni una prueba de penetración del host en este incremento.
