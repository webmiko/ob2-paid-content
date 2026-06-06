#!/bin/bash
set -euo pipefail

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
