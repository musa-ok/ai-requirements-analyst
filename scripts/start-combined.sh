#!/usr/bin/env sh
# Tek DigitalOcean bileşeni: FastAPI (localhost) + Django gunicorn
set -e

export FASTAPI_BASE_URL="${FASTAPI_BASE_URL:-http://127.0.0.1:8001}"

uvicorn backend.main:app --host 127.0.0.1 --port 8001 &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

python manage.py migrate --noinput
exec gunicorn ai_ra_saas.wsgi \
  --bind "0.0.0.0:${PORT:-8080}" \
  --workers 1 \
  --timeout 180 \
  --graceful-timeout 30
