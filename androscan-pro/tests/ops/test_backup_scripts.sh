#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

bash -n "$ROOT/scripts/backup.sh"
bash -n "$ROOT/scripts/restore.sh"

# Prepara un conjunto ficticio de archivos para comprobar que la cancelación
# ocurre antes de ejecutar cualquier comando Docker destructivo.
BACKUP="$TMP/backup"
mkdir -p "$BACKUP" "$TMP/bin"
printf 'test dump\n' > "$BACKUP/postgres.dump"
printf 'test objects\n' > "$BACKUP/minio-data.tar.gz"
printf 'compose\n' > "$BACKUP/docker-compose.yml"
printf 'env example\n' > "$BACKUP/env.example"
printf 'readme\n' > "$BACKUP/README-RESPALDO.txt"
(cd "$BACKUP" && sha256sum postgres.dump minio-data.tar.gz docker-compose.yml env.example README-RESPALDO.txt > SHA256SUMS)
cat > "$TMP/bin/docker" <<'MOCK'
#!/usr/bin/env sh
echo "$*" >> "$DOCKER_CALL_LOG"
exit 0
MOCK
chmod +x "$TMP/bin/docker"
export DOCKER_CALL_LOG="$TMP/docker.log"
export PATH="$TMP/bin:$PATH"
printf 'no\n' | "$ROOT/scripts/restore.sh" "$BACKUP" > "$TMP/output.txt"
[[ ! -s "$DOCKER_CALL_LOG" ]] || { echo "ERROR: Docker fue invocado tras cancelar." >&2; exit 1; }
grep -q 'Cancelado' "$TMP/output.txt"
echo 'OK: sintaxis shell y cancelación segura verificadas.'
