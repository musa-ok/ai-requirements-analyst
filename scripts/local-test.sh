#!/usr/bin/env bash
# Hizli lokal dogrulama — servisleri baslatmaz, test + health kontrol eder.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> pytest (contract + health)"
python -m pytest requirements_app/tests.py tests/test_health.py tests/test_integration.py -q

echo "==> django tests"
python manage.py test requirements_app -v 0

echo "==> behave"
behave features/requirement_analysis.feature --no-capture

API_URL="${API_URL:-http://127.0.0.1:8001}"
if curl -sf "${API_URL}/health" >/dev/null 2>&1; then
  echo "==> FastAPI health OK (${API_URL})"
else
  echo "==> FastAPI calismiyor (${API_URL}) — Terminal B: uvicorn backend.main:app --port 8001"
fi

echo ""
echo "Manuel UI testi:"
echo "  Django:  FASTAPI_BASE_URL=http://127.0.0.1:8001 python manage.py runserver"
echo "  SPA:     cd frontend && python3 -m http.server 5500"
echo "  Deploy:  DEPLOYMENT_DO.md"
