#!/bin/bash
set -euo pipefail

python manage.py migrate --noinput
python manage.py shell -c "from config.cache import ensure_database_cache_table; ensure_database_cache_table()"
python manage.py collectstatic --noinput

exec "$@"
