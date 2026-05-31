# AI-RA — Lokal Test ve DigitalOcean Deploy

Bu rehber: önce makinede doğrulama, sonra **DigitalOcean App Platform**’a iki servis (Django + FastAPI) deploy.

---

## 1) Lokal test (3 terminal)

### Terminal A — Sanal ortam (bir kez)

```bash
cd /path/to/ai-requirements-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

### Terminal B — FastAPI (AI + export)

```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
```

Kontrol:

```bash
curl -s http://127.0.0.1:8001/health
# {"status":"ok"}
```

### Terminal C — Django (web UI)

```bash
source .venv/bin/activate
export FASTAPI_BASE_URL=http://127.0.0.1:8001
python manage.py runserver 127.0.0.1:8000
```

Tarayıcı: **http://127.0.0.1:8000/requirements/new/**

1. ⚙️ **Ayarlar** → model + API anahtarı → Kaydet  
2. Gereksinim yaz → **Analiz Et**  
3. Sonuç sayfasında **PDF / Word / Markdown** dene  

### Terminal D (isteğe bağlı) — SPA

```bash
cd frontend && python3 -m http.server 5500
```

Tarayıcı: **http://127.0.0.1:5500**  
Ayarlar → Backend URL: `http://127.0.0.1:8001` + API key.

---

## 2) Otomatik test komutları

```bash
source .venv/bin/activate
python -m pytest requirements_app/tests.py tests/test_health.py tests/test_integration.py -q
python manage.py test requirements_app
behave features/requirement_analysis.feature
```

Gerçek Gemini ile entegrasyon (opsiyonel):

```bash
export TEST_GEMINI_API_KEY=your-key
python -m pytest -m integration
```

---

## 3) DigitalOcean App Platform mimarisi

| Bileşen | Komut | Port |
|---------|--------|------|
| **django** | `sh scripts/start-django.sh` (migrate + gunicorn) | `$PORT` (8080) |
| **api** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` | `$PORT` |

Build (Django):

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Build (API):

```bash
pip install -r requirements.txt
```

Şablon spec: [`.do/app.yaml`](.do/app.yaml)

---

## 4) DO kurulum adımları

1. [DigitalOcean](https://cloud.digitalocean.com/) → **Apps** → **Create App** → GitHub repo bağla.
2. **İki Web Service** ekle (aynı repo, farklı isim/komut):

   **Service: `django`**
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Run: `sh scripts/start-django.sh`
   - Health: `/` (200)
   - Env:
     - `DEBUG=False`
     - `SECRET_KEY` → **Encrypt** (güçlü rastgele)
     - `ALLOWED_HOSTS` → `django-xxx.ondigitalocean.app` (kendi domain’in)
     - `FASTAPI_BASE_URL` → `https://api-xxx.ondigitalocean.app` (API servis URL’si)

   **Service: `api`**
   - Build: `pip install -r requirements.txt`
   - Run: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/health`
   - Env:
     - `CORS_ALLOW_ORIGINS` → `https://django-xxx.ondigitalocean.app,https://spa-domain.com`
     - `CHROMA_PERSIST_DIR` → `/data/chroma` (aşağıdaki volume ile)

3. **API servisine Volume** (RAG kalıcılığı, opsiyonel ama önerilir):
   - Mount path: `/data`
   - Size: 1 GB
   - `CHROMA_PERSIST_DIR=/data/chroma`

4. Deploy → smoke test:

```bash
curl -s https://api-xxx.ondigitalocean.app/health
curl -sI https://django-xxx.ondigitalocean.app/
```

5. Django Ayarlar / SPA’da **Backend API URL** = API servisinin public HTTPS adresi.

---

## 5) Ortam değişkenleri özeti

| Değişken | Servis | Zorunlu (prod) |
|----------|--------|----------------|
| `SECRET_KEY` | django | Evet |
| `DEBUG` | django | `False` |
| `ALLOWED_HOSTS` | django | Evet (domain) |
| `FASTAPI_BASE_URL` | django | Evet (export köprüsü) |
| `CORS_ALLOW_ORIGINS` | api | Evet (UI origin’leri) |
| `CHROMA_PERSIST_DIR` | api | Önerilir |
| LLM `api_key` | — | **Hayır** (istemciden gelir) |

---

## 6) Sık hatalar

| Belirti | Çözüm |
|---------|--------|
| SPA/Django analiz 404 | Backend URL yanlış (8000 ≠ FastAPI); `8001` veya DO API URL |
| Export PDF 404 | `FASTAPI_BASE_URL` Django’da yanlış veya analiz register olmamış |
| CORS hatası | `CORS_ALLOW_ORIGINS`’e Django/SPA HTTPS origin ekle |
| Deploy timeout | API health `/health` — LangChain boot’ta yüklenmez (lazy) |
| `tokenizers` / pip build fail | `runtime.txt` (Python 3.11); Chroma opsiyonel — `requirements-rag.txt` |
| `ImproperlyConfigured` | Prod’da `SECRET_KEY` ve `ALLOWED_HOSTS` set et |

---

## 7) SPA’yı DO’da yayınlama (opsiyonel)

**Static Site** bileşeni: `frontend/` klasörü, build yok.  
Ayarlar → Backend URL = API servisi HTTPS.

Alternatif: Django `static/` altına SPA kopyalamak (tek domain) — şu an repo’da ayrı tutuluyor.
