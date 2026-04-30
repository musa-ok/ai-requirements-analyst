# Implementation Summary — AI_RA İlk SaaS Prototipi

## Proje Adı
Yapay Zekâ Destekli Gereksinim Analisti Sistemi (AI_RA)

## Amaç
Kullanıcıların doğal dilde ifade ettiği yazılım gereksinim fikirlerini otomatik olarak BDD formatında yapılandırılmış gereksinime, Gherkin test senaryosuna ve Story Point tahminlerine dönüştürmek.

---

## Kullanılan Teknolojiler

- **Django 4.2**: MVT (Model-View-Template) web framework
- **SQLite**: Geliştirme ortamı kalıcı veritabanı
- **Python 3.10+**: Uygulama dili
- **HTML5 / CSS3**: Template tabanlı sunum katmanı
- **pytest + pytest-django**: Unit ve functional testler
- **behave**: BDD acceptance testleri
- **gunicorn**: WSGI production server
- **whitenoise**: Statik dosya servisi (production)
- **Render.com**: Bulut deployment platformu

---

## MVC/MVT Yapısı

Django MVT mimarisi aşağıdaki şekilde uygulanmıştır:

| MVC Karşılığı | Django Karşılığı | Dosya |
|---------------|-----------------|-------|
| Model | Model | `requirements_app/models.py` |
| View (Sunum) | Template | `requirements_app/templates/` |
| Controller | View + URL | `requirements_app/views.py` + `urls.py` |

---

## 3-Tier Mimari Karşılığı

| Katman | Django Karşılığı | Açıklama |
|--------|-----------------|----------|
| Presentation Tier | HTML/CSS Templates | Kullanıcı tarayıcıda görür |
| Logic Tier | Views + Services | `views.py`, `services.py` |
| Persistence Tier | Django ORM + SQLite | `models.py`, `db.sqlite3` |

---

## Sayfalar

1. **Ana Sayfa** (`/`) — Proje tanıtımı, son analizler, navigasyon
2. **Gereksinim Formu** (`/requirements/new/`) — Proje adı ve gereksinim metni girişi
3. **Sonuç Sayfası** (`/requirements/<id>/`) — BDD, Gherkin, QA ve Story Point çıktıları
4. **Liste Sayfası** (`/requirements/`) — Geçmiş analizler tablosu

---

## Veritabanı Modelleri

### Project
- `id`, `name`, `description`, `created_at`

### Requirement
- `id`, `project` (FK), `raw_text`, `status`, `created_at`

### AnalysisResult
- `id`, `requirement` (OneToOne), `bdd_output`, `gherkin_output`, `qa_result`, `story_point`, `created_at`

---

## Servis Katmanı (services.py)

| Fonksiyon | Açıklama |
|-----------|----------|
| `generate_bdd_output(text)` | Given-When-Then formatında çıktı üretir |
| `generate_gherkin_output(text)` | Feature/Scenario Gherkin senaryosu üretir |
| `run_qa_validation(text)` | Gereksinim kalitesini doğrular |
| `estimate_story_points(text)` | Karmaşıklığa göre SP tahmini yapar |
| `analyze_requirement(text)` | Tüm analizi birleştirir ve döndürür |

---

## RESTful Routing

| HTTP Method | URL | İşlev |
|-------------|-----|-------|
| GET | `/` | Ana sayfa |
| GET | `/requirements/` | Kaynak listesi |
| GET | `/requirements/new/` | Yeni kaynak formu |
| POST | `/requirements/new/` | Kaynak oluştur |
| GET | `/requirements/<id>/` | Kaynak detayı |

---

## Test Yaklaşımı

- **Unit Testler**: `services.py` fonksiyonları, model oluşturma, form doğrulama
- **Functional Testler**: HTTP istek/yanıt doğrulama, template kontrolü, yönlendirme
- **BDD Acceptance Testleri**: `behave` ile `.feature` dosyasından çalışan senaryo testleri

---

## Deploy Bilgisi

- Platform: Render.com (Free Tier)
- URL: https://ai-ra-saas.onrender.com
- Build: `pip install -r requirements.txt && python manage.py migrate --run-syncdb`
- Start: `gunicorn ai_ra_saas.wsgi --log-file -`

---

## Yerel Çalıştırma Komutları

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

:: Test komutları
python manage.py test
pytest
behave
```
