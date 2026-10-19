# F9.15 — Respaldos y recuperación

## Objetivo y alcance

Este incremento incorpora procedimientos operativos para respaldar/restaurar los dos almacenes persistentes principales del despliegue de desarrollo: PostgreSQL y el volumen de datos de MinIO. También archiva `docker-compose.yml` y `.env.example` como referencia de configuración no secreta.

**No es una solución de recuperación ante desastres completa.** El respaldo se crea localmente, no se cifra automáticamente y no se copia por sí solo a otro servidor. El archivo `.env` real, claves JWT, credenciales S3 y secretos se excluyen deliberadamente; deben mantenerse en un gestor seguro y respaldarse por separado mediante el procedimiento aprobado por la organización.

## Requisitos previos

- Docker Engine y Docker Compose plugin instalados.
- Servicios `postgres` y `minio` creados por el `docker compose.yml` de este proyecto.
- Espacio disponible para el dump y el archivo de datos de MinIO.
- Acceso restringido al directorio de respaldo. Para producción, usar un destino cifrado y fuera del host principal.
- La imagen auxiliar `alpine:3.20` disponible localmente o posibilidad de descargarla. Puede cambiarse con `BACKUP_HELPER_IMAGE`.

## Crear un respaldo

Desde la raíz del proyecto:

```bash
./scripts/backup.sh
```

Opcionalmente, indicar una carpeta destino:

```bash
./scripts/backup.sh /ruta/segura/respaldos
```

El script genera una carpeta con fecha UTC que incluye:

- `postgres.dump`: formato custom de `pg_dump`.
- `minio-data.tar.gz`: copia del contenido del volumen de datos de MinIO.
- `docker-compose.yml` y `env.example`: referencias de configuración sin secretos reales.
- `SHA256SUMS`: hashes de integridad de los archivos del respaldo.

Después de generarlo, copie el directorio a un destino independiente y cifrado. No considere un respaldo local en el mismo disco como suficiente para recuperación ante pérdida del host.

## Restaurar

> **Operación destructiva.** La restauración reemplaza los datos de la base de datos y el contenido de MinIO. Antes de ejecutarla, respalde el estado actual y confirme que está trabajando contra el entorno correcto.

```bash
./scripts/restore.sh /ruta/segura/respaldos/androscan-AAAAMMDDTHHMMSSZ
```

El script verifica los hashes y exige escribir exactamente `RESTORE`. Luego ejecuta `pg_restore`, detiene MinIO, sustituye el contenido de su volumen por el archivo archivado y vuelve a iniciar MinIO. No restaura el `.env` ni cambia automáticamente la configuración de secretos.

## Comprobaciones posteriores

1. Verifique `docker compose ps` y los logs de `postgres`, `minio`, `api` y `worker`.
2. Compruebe `GET /api/v1/health/live` y `GET /api/v1/health/ready`.
3. Inicie sesión y confirme que las organizaciones y aplicaciones esperadas existen.
4. Confirme que una APK previamente almacenada sigue disponible y que sus análisis e informes se pueden consultar.
5. Ejecute una prueba controlada de análisis y descarga de informe antes de devolver el servicio a usuarios.
6. Registre fecha, duración, operador, incidencias y resultado de la restauración.

## Frecuencia y retención: propuesta pendiente de aprobación operativa

Para un piloto, considerar respaldo diario y una copia semanal fuera del host. La retención, cifrado, RPO/RTO, ubicación externa y periodicidad de pruebas de restauración deben acordarse con el responsable del servicio antes de producción. No se aplica borrado automático de respaldos en esta fase.

## Limitaciones conocidas

- El script copia el volumen de MinIO directamente; es necesario detener escrituras o programar la operación durante una ventana de mantenimiento para evitar inconsistencias entre PostgreSQL y objetos.
- No hay cifrado, envío externo, rotación de claves, retención automática, alertas de fallos ni restauración automatizada validada en un entorno completo.
- La restauración de PostgreSQL y MinIO no es transaccional como conjunto; si una etapa falla, se debe detener la recuperación y verificar manualmente ambos almacenes.
- El contenido de `.env` y cualquier secreto se deben recuperar por un canal seguro separado.
