# Trazabilidad F9.15 — Respaldos y recuperación

| Requisito operativo | Implementación | Evidencia/estado |
|---|---|---|
| Respaldar PostgreSQL | `scripts/backup.sh` usa `pg_dump -Fc` desde el contenedor | Implementado; sintaxis shell validable |
| Respaldar objetos MinIO | Archivo tar del volumen con contenedor auxiliar | Implementado; requiere contenedores y Docker disponibles |
| Integridad de artefactos | `SHA256SUMS` y verificación antes de restaurar | Implementado |
| Confirmación ante restauración destructiva | Requiere escribir `RESTORE` | Implementado |
| No incluir secretos automáticamente | Se excluye `.env`; solo se copia `.env.example` | Implementado |
| Procedimiento de verificación post-restauración | Guía de operación | Documentado; no equivale a una restauración integral ejecutada |
| Copia externa cifrada y retención | Procedimiento manual/política pendiente | Pendiente |
| Prueba de recuperación de extremo a extremo | Requiere instancia Docker con datos de prueba | No ejecutada en este entorno |
