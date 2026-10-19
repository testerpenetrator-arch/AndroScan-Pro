#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${1:-}"
HELPER_IMAGE="${BACKUP_HELPER_IMAGE:-alpine:3.20}"

if [[ -z "$BACKUP_DIR" || ! -d "$BACKUP_DIR" ]]; then
  echo "Uso: $0 /ruta/al/directorio/androscan-AAAAMMDDTHHMMSSZ" >&2
  exit 2
fi
BACKUP_DIR="$(cd "$BACKUP_DIR" && pwd)"
for f in postgres.dump apk-storage.tar.gz docker-compose.yml env.example SHA256SUMS; do
  [[ -s "$BACKUP_DIR/$f" ]] || { echo "ERROR: falta o está vacío: $f" >&2; exit 1; }
done
command -v docker >/dev/null || { echo "ERROR: docker no está instalado." >&2; exit 1; }
(cd "$BACKUP_DIR" && sha256sum -c SHA256SUMS)

cat <<'WARN'
ADVERTENCIA: la restauración reemplaza los datos actuales de PostgreSQL y los APK almacenados en el volumen local.
Realice primero un respaldo del estado actual. No continúe si no está seguro de la organización/instancia destino.
WARN
read -r -p 'Escriba exactamente RESTORE para continuar: ' CONFIRM
[[ "$CONFIRM" == "RESTORE" ]] || { echo "Cancelado; no se modificaron datos."; exit 0; }

cd "$PROJECT_ROOT"

echo "[1/3] Restaurando PostgreSQL (los datos actuales se reemplazarán)..."
docker compose exec -T postgres sh -lc 'pg_restore --clean --if-exists --no-owner --no-privileges --username="$POSTGRES_USER" --dbname="$POSTGRES_DB"' < "$BACKUP_DIR/postgres.dump"

echo "[2/3] Deteniendo API y worker para evitar escrituras..."
docker compose stop api worker
API_ID="$(docker compose ps -a -q api | head -n1)"
[[ -n "$API_ID" ]] || { echo "ERROR: no se encontró el contenedor API para acceder al volumen." >&2; exit 1; }

echo "[3/3] Restaurando el volumen de APK..."
docker run --rm --volumes-from "$API_ID" -v "$BACKUP_DIR:/backup:ro" "$HELPER_IMAGE" \
  sh -ec 'find /data/apks -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +; tar -xzf /backup/apk-storage.tar.gz -C /data/apks'
docker compose start api worker

echo "Restauración finalizada. Compruebe API, health checks, análisis e informes antes de reanudar el servicio normal."
