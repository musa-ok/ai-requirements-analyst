#!/usr/bin/env sh
set -e
python manage.py migrate --noinput
exec gunicorn ai_ra_saas.wsgi --bind "0.0.0.0:${PORT:-8080}" --workers 2
