#!/usr/bin/env bash
set -Eeuo pipefail

# Ejecutar desde cualquier directorio: el proyecto se resuelve desde este script.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${1:-$PROJECT_ROOT/backups}"
HELPER_IMAGE="${BACKUP_HELPER_IMAGE:-alpine:3.20}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$BACKUP_DIR/androscan-$STAMP"

command -v docker >/dev/null || { echo "ERROR: docker no está instalado." >&2; exit 1; }
mkdir -p "$BACKUP_DIR"
mkdir "$DEST"
cd "$PROJECT_ROOT"

cleanup() { if [[ -d "$DEST" && -z "$(find "$DEST" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then rmdir "$DEST"; fi; }
trap cleanup ERR

echo "[1/4] Exportando PostgreSQL..."
docker compose exec -T postgres sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$DEST/postgres.dump"
test -s "$DEST/postgres.dump"

echo "[2/4] Respaldando APK del volumen compartido..."
API_ID="$(docker compose ps -q api)"
[[ -n "$API_ID" ]] || { echo "ERROR: el contenedor API no está creado/en ejecución." >&2; exit 1; }
docker run --rm --volumes-from "$API_ID":ro -v "$DEST:/backup" "$HELPER_IMAGE" \
  sh -ec 'tar -czf /backup/apk-storage.tar.gz -C /data/apks .'
test -s "$DEST/apk-storage.tar.gz"

echo "[3/4] Guardando manifiesto de configuración no secreta..."
cp docker-compose.yml "$DEST/docker-compose.yml"
cp .env.example "$DEST/env.example"
cat > "$DEST/README-RESPALDO.txt" <<INFO
AndroScan — respaldo creado en UTC: $STAMP
Contenido: postgres.dump (formato custom de pg_dump), apk-storage.tar.gz, docker-compose.yml y env.example.
No se incluye el archivo .env real ni secretos. Resguárdelos por separado en un gestor seguro.
Restauración: scripts/restore.sh "$DEST" (requiere confirmación interactiva RESTORE).
Este respaldo no cifra los archivos. Almacénelo en un destino cifrado y con acceso restringido.
INFO

echo "[4/4] Calculando hashes SHA-256..."
(cd "$DEST" && sha256sum postgres.dump apk-storage.tar.gz docker-compose.yml env.example README-RESPALDO.txt > SHA256SUMS)
trap - ERR
echo "Respaldo completado: $DEST"
echo "Verifique SHA256SUMS y copie el respaldo a un destino externo seguro."
