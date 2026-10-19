#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/.env"
command -v openssl >/dev/null || { echo "ERROR: se requiere openssl para generar secretos." >&2; exit 1; }
if [[ -e "$ENV_FILE" ]]; then
  echo "ERROR: $ENV_FILE ya existe; no se sobrescribirá." >&2
  exit 2
fi
umask 077
JWT_SECRET="$(openssl rand -hex 32)"
DB_PASSWORD="$(openssl rand -hex 24)"
cat > "$ENV_FILE" <<ENV
APP_NAME=AndroScan API
APP_ENV=development
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg://androscan:${DB_PASSWORD}@postgres:5432/androscan
REDIS_URL=redis://redis:6379/0
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/data/apks
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=androscan
S3_SECRET_KEY=$(openssl rand -hex 24)
S3_BUCKET=androscan-apks
S3_REGION=us-east-1
JWT_SECRET_KEY=${JWT_SECRET}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
MAX_APK_SIZE_MB=100
SANDBOX_IMAGE=androscan/sandbox-tools:0.1
SANDBOX_CPU=1.0
SANDBOX_MEMORY_MB=1024
SANDBOX_PIDS=128
SANDBOX_TIMEOUT_SECONDS=900
SANDBOX_STORAGE_MB=2048
POSTGRES_PASSWORD=${DB_PASSWORD}
ENV
chmod 600 "$ENV_FILE"
echo "Archivo .env creado con permisos 600 y secretos aleatorios. No lo compartas ni lo subas al repositorio."
echo "Para producción, configura APP_ENV=production y sigue docs/endurecimiento-despliegue-f916.md."
