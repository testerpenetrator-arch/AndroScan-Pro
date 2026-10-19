#!/usr/bin/env bash
# Validación local repetible del proyecto AndroScan.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

printf '\n==> Sintaxis de scripts Bash\n'
for script in scripts/*.sh; do bash -n "$script"; done

printf '\n==> Compilación sintáctica Python\n'
python3 -m compileall -q backend/app backend/tests

printf '\n==> Pruebas automatizadas del backend\n'
(
  cd backend
  PYTHONPATH=. python3 -m pytest -q
)

printf '\n==> Cabeza de migraciones Alembic\n'
(
  cd backend
  alembic heads
)

if [[ -d frontend/node_modules ]]; then
  printf '\n==> Construcción del frontend (dependencias ya instaladas)\n'
  (cd frontend && npm run build)
else
  printf '\nAVISO: frontend no construido; falta frontend/node_modules. Ejecuta npm install y npm run build con conectividad.\n'
fi

printf '\nValidaciones locales completadas. La prueba de despliegue Docker requiere Docker Engine y no forma parte de este script.\n'
