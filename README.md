# AI_RA — Yapay Zekâ Destekli Gereksinim Analisti Sistemi
## İlk SaaS Prototipi

---

## Proje Tanımı

AI_RA, kullanıcıların doğal dilde ifade ettiği yazılım fikirlerini BDD formatında yapılandırılmış gereksinime, Gherkin test senaryosuna ve Story Point tahminlerine dönüştüren web tabanlı bir SaaS uygulamasıdır.

Bu prototip, sistemi MVP (Minimum Viable Product) kapsamında gerçekleştirir; canlı Gemini API bağlantısı olmadan deterministik analiz servisi ile çalışır.

---

## Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Backend | Django 4.2 (Python) |
| Veritabanı | SQLite (prototip), PostgreSQL'e geçiş hazır |
| Frontend | HTML5 / CSS3 (template tabanlı) |
| Test | pytest, pytest-django, behave |
| Deploy | Render.com |

---

## Mimari

Bu prototip **3-tier mimari** ve **MVC/MVT** prensipleri üzerine inşa edilmiştir:

```
Presentation Tier  →  HTML/CSS Templates (requirements_app/templates/)
Logic Tier         →  Django Views + Services (views.py, services.py)
Persistence Tier   →  SQLite / Django ORM (models.py)
```

HTTP istek-yanıt döngüsü:
```
Tarayıcı → HTTP Request → Django URL Router → View/Controller → Template → HTTP Response
```

---

## Kurulum

```bash
# 1. Sanal ortam oluştur ve aktive et
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Veritabanını hazırla
python manage.py migrate

# 4. Uygulamayı başlat
python manage.py runserver
```

Tarayıcıda aç: http://127.0.0.1:8000

---

## Sayfalar ve URL'ler

| URL | Açıklama |
|-----|----------|
| `/` | Ana sayfa |
| `/requirements/new/` | Yeni gereksinim analizi formu |
| `/requirements/<id>/` | Analiz sonuç sayfası |
| `/requirements/` | Geçmiş analizler listesi |

---

## Testleri Çalıştırma

### Django Unit & Functional Testler
```bash
python manage.py test
```

### pytest ile
```bash
pytest
```

### BDD Acceptance Testleri (behave)
```bash
behave
```

---

## Deployment (Render.com)

1. Render.com üzerinde yeni bir **Web Service** oluştur.
2. GitHub reposunu bağla.
3. Build komutu: `pip install -r requirements.txt && python manage.py migrate --run-syncdb`
4. Start komutu: `gunicorn ai_ra_saas.wsgi --log-file -`
5. Environment: `DJANGO_SETTINGS_MODULE=ai_ra_saas.settings`

Deploy linki: https://ai-ra-saas.onrender.com

---

## Ekip

| Rol | İsim |
|-----|------|
| Takım Lideri | Muhammed Sina GÜN |
| Geliştirici | Seyyid Muhammed SUN |
| Geliştirici | Musa OK |
| Geliştirici | Şahin KARA |
| Test Uzmanı | Berk KIZGIN |
| Eğitmen | Prof. Dr. Haluk Gümüşkaya |

---

## Kurs Bilgisi

HW5 — Yazılım Mühendisliği Dersi  
İlk SaaS Prototip Teslimi
