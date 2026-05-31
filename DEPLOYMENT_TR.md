# AI-RA Railway Deployment Rehberi (TR)

Bu rehber, projeyi son yayin oncesi Railway uzerinde guvenli ve tekrar edilebilir sekilde ayaga kaldirmak icin hazirlanmistir.

## 1) On Kosullar

- Railway hesabi
- GitHub repository baglantisi
- Projede `Procfile` mevcut olmasi (`web: gunicorn ai_ra_saas.wsgi --log-file -`)
- Lokal ortamda son degisikliklerin repoya aktarilmis olmasi

## 2) Mimari Karari (Hybrid: Django + FastAPI)

Bu repoda iki runtime vardir:

- Django (SaaS UI): `ai_ra_saas.wsgi` uzerinden Gunicorn ile
- FastAPI (AI Core): `backend.main:app` uzerinden Uvicorn ile

Railway uzerinde en temiz kurulum:

- Service-1: `web-django` (Procfile ile)
- Service-2: `api-fastapi` (ozel start command ile)

> Not: Mevcut `Procfile` Django service icin dogrudan kullanilir.

## 3) Railway Proje Kurulumu

1. Railway dashboard -> **New Project** -> **Deploy from GitHub Repo**
2. Bu repository'yi secin.
3. Ilk service olarak `web-django` olusturun (Railway `Procfile` komutunu otomatik algilar).
4. Ayni repodan ikinci service olarak `api-fastapi` ekleyin.

## 4) Build ve Start Komutlari

### 4.1 Django Service (`web-django`)

- Build Command:
  - `pip install -r requirements.txt`
- Start Command:
  - Bos birakilabilir; Railway `Procfile` komutunu kullanir.
  - Alternatif acik tanim: `gunicorn ai_ra_saas.wsgi --log-file -`

### 4.2 FastAPI Service (`api-fastapi`)

- Build Command:
  - `pip install -r requirements.txt`
- Start Command:
  - `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

## 5) Ortam Degiskenleri (Environment Variables)

Railway -> ilgili service -> **Variables** alanindan girin.

### 5.1 Ortak / Guvenlik

- `SECRET_KEY`: Django secret key (**production zorunlu** — varsayilan anahtar DEBUG=False iken reddedilir)
- `DEBUG`: `False` (prod)
- `ALLOWED_HOSTS`: deploy domain(leri)
- `FASTAPI_BASE_URL`: Django servisinin export kaydi icin FastAPI adresi (ornek: `https://ai-ra-api.onrender.com`)

### 5.2 LLM / Gemini (stateless)

API anahtarlari **sunucu ortam degiskeninden okunmaz**. Istemci (SPA veya form) her `/analyze` isteginde JSON govdesinde `api_key` gonderir.

Opsiyonel (yalnizca lokal entegrasyon testleri icin):

- `TEST_GEMINI_API_KEY`: `pytest -m integration` fixture'lari icin

### 5.3 Jira Export

- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `JIRA_PROJECT_KEY`

### 5.4 FastAPI servisi

- `CORS_ALLOW_ORIGINS`: SPA/Django origin listesi (virgülle ayrılmış)
- `CHROMA_PERSIST_DIR`: RAG indeksi için disk yolu (Render disk mount önerilir)

### 5.5 GitHub Export (istemci / entegrasyon testleri)

- `GITHUB_TOKEN` (repo write yetkili)
- `GITHUB_REPOSITORY` (ornek: `org/repo`)

## 6) Release Oncesi Test Stratejisi

Testler iki seviyeye ayrilmistir:

- **Contract/Fast Testler**: varsayilan `pytest` kosusunda calisir.
- **Integration Testler** (`@pytest.mark.integration`): Chroma/Gemini/Jira gibi agir ve dis bagimli akislari kapsar.

Onerilen komutlar:

- Hizli CI (default):
  - `python -m pytest`
- Sadece contract testleri:
  - `python -m pytest -m contract`
- Tam entegrasyon (manual/stage):
  - `python -m pytest -m integration`
- Gercek dis API dahil:
  - `python -m pytest -m "integration and external_api"`

## 7) Stateless Dogrulama Kontrol Listesi

- FastAPI analiz ciktilari sadece process memory (`session_store`) icinde tutulur.
- Django tarafinda analiz kayitlari cookie-session uzerinde tutulur; SQLite'a analiz sonucu persist edilmez.
- Export endpointleri (`/export/pdf`, `/export/jira`, `/export/github`) ciktilari session memory verisinden uretir.

## 8) Deployment Sonrasi Smoke Test

1. Django endpoint:
   - `GET /` -> 200
2. FastAPI health:
   - `GET /health` -> `{"status":"ok"}`
   - `GET /` -> `{"status":"ok"}`
3. Analyze akisi:
   - `POST /analyze` ile ornek requirement gonderin.
4. Export akisi:
   - `GET /export/pdf/{session_id}/{analysis_id}` -> PDF
   - `POST /export/jira/{session_id}` -> jira issue key donmeli
   - `POST /export/github/{session_id}` -> status `ok`

## 9) Onerilen Operasyonel Ayarlar

- Railway auto-deploy: sadece `main` branch
- Rollback icin onceki stable release tag'i kullanin
- API key rotation: en az 90 gunde bir
- Log takip: deploy sonrasi ilk 15 dakika aktif izleme

## 10) Kisa Go-Live Plani

1. `main` branch temiz ve testleri yesil hale getirin.
2. Railway'de iki service'in de build/deploy durumunu kontrol edin.
3. Env var'lari dogru service'lere girin.
4. Smoke testleri tamamlayin.
5. Production trafik acin.

