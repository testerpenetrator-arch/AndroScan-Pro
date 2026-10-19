#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-$ROOT/.env}"
[[ -f "$ENV_FILE" ]] || { echo "ERROR: no existe $ENV_FILE. Ejecuta scripts/init-secrets.sh." >&2; exit 1; }
python3 - "$ENV_FILE" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
values = {}
for line in p.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    values[k.strip()] = v.strip().strip('"').strip("'")
errors = []
for key in ('JWT_SECRET_KEY', 'POSTGRES_PASSWORD', 'S3_SECRET_KEY'):
    value = values.get(key, '')
    if not value or value.lower() in {'changeme', 'change-me', 'replace-with-a-random-secret', 'androscan-development-only', 'androscan'}:
        errors.append(f'{key}: ausente o valor predeterminado inseguro')
if len(values.get('JWT_SECRET_KEY', '')) < 32:
    errors.append('JWT_SECRET_KEY: debe tener al menos 32 caracteres')
if values.get('APP_ENV', 'development').lower() == 'production':
    if values.get('DEBUG', '').lower() in {'1', 'true', 'yes'}:
        errors.append('DEBUG no puede estar habilitado en producción')
if errors:
    print('Validación de entorno fallida:')
    print('\n'.join(f'- {e}' for e in errors))
    sys.exit(1)
print('Validación básica de variables y secretos aprobada.')
PY
