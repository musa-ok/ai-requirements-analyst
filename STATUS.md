# AI-RA — Proje Durumu (2026)

## Mimari

| Bileşen | Teknoloji | Rol |
|---------|-----------|-----|
| Django UI | Django 4.2 + SQLite | Form, oturum tabanlı sonuç listesi |
| FastAPI AI | LangGraph + Gemini/Claude/GPT | Analiz, RAG, PDF/Word/Jira/GitHub export |
| SPA | `frontend/` | Tam özellikli istemci (çoklu model, export) |

Analiz sonuçları **veritabanına yazılmaz**; Django signed-cookie session, FastAPI process memory (`session_store`).

## Tamamlanan özellikler

- Stateless LLM: API anahtarı istemciden (`api_key` JSON)
- Lazy boot: LangChain yalnızca ilk `/analyze` isteğinde yüklenir
- Django ↔ FastAPI export köprüsü: `POST /analysis/register` + sonuç sayfasında PDF/Word/Jira/GitHub
- Ayarlar: SPA ve Django header aynı `localStorage` anahtarı (`ai_ra_user_config`)
- CI: `.github/workflows/ci.yml` (Django + pytest + behave)
- Deploy şablonu: `render.yaml` (Django + FastAPI iki servis)
- Opsiyonel Chroma kalıcılığı: `CHROMA_PERSIST_DIR`

## Bilinen sınırlar

- FastAPI `session_store` restart / çok worker’da sıfırlanır (Redis/DB ileride)
- Django ve FastAPI ayrı servislerdeyse export için `FASTAPI_BASE_URL` zorunlu
- PostgreSQL dokümantasyonda geçer; üretimde henüz yapılandırılmadı (SQLite + session)

## Testler

```bash
python -m pytest                    # contract + health (varsayılan)
python manage.py test requirements_app
behave features/requirement_analysis.feature
python -m pytest -m integration     # gerçek LLM / Chroma (anahtar gerekir)
```

## Lokal çalıştırma

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
cd frontend && python3 -m http.server 5500
python manage.py runserver          # Django :8000
```

Detay: `README.md`, `DEPLOYMENT_TR.md`, `.env.example`
