# Mimari Açıklama — AI_RA İlk SaaS Prototipi

## Genel Yapı

Bu prototip, **client-server web mimarisi** temelinde geliştirilmiştir.

Kullanıcı tarayıcı üzerinden **HTTP istekleri** gönderir. Django uygulaması bu istekleri **URL routing** mekanizmasıyla ilgili **view/controller** fonksiyonlarına yönlendirir. Sunum katmanı **HTML/CSS template** dosyalarından, iş mantığı katmanı **Django view ve servis fonksiyonlarından**, kalıcılık katmanı ise **SQLite veritabanından** oluşur.

Bu yapı, SaaS uygulamalarında kullanılan aşağıdaki mimari ilkelerle tam uyumludur:

- **3-Tier Architecture**
- **MVC/MVT Organization**
- **RESTful Resource Handling**
- **Template-Based Views**
- **Persistence**

---

## 3-Tier Architecture

```
┌──────────────────────────────────────┐
│         Presentation Tier            │
│  HTML/CSS Templates (Tarayıcı)       │
│  home.html, requirement_form.html,   │
│  requirement_detail.html, list.html  │
└────────────────┬─────────────────────┘
                 │ HTTP Request / Response
┌────────────────▼─────────────────────┐
│            Logic Tier                │
│  Django Views (views.py)             │
│  Servis Katmanı (services.py)        │
│  URL Routing (urls.py)               │
│  Form Doğrulama (forms.py)           │
└────────────────┬─────────────────────┘
                 │ Django ORM Sorguları
┌────────────────▼─────────────────────┐
│          Persistence Tier            │
│  Django ORM (models.py)              │
│  SQLite Veritabanı (db.sqlite3)      │
│  Project, Requirement, AnalysisResult│
└──────────────────────────────────────┘
```

---

## HTTP Request / Response Döngüsü

```
Kullanıcı (Tarayıcı)
        │
        │  GET /requirements/new/
        ▼
Django URL Router (urls.py)
        │
        │  requirement_new view fonksiyonuna yönlendir
        ▼
View / Controller (views.py)
        │
        │  Template render et
        ▼
HTML Template (requirement_form.html)
        │
        │  HTTP Response (200 OK + HTML)
        ▼
Kullanıcı Formu Doldurur

        │  POST /requirements/new/ (form verisi)
        ▼
Django URL Router
        │
        ▼
View — Form doğrula → Services çağır → DB kaydet
        │
        │  HTTP Response (302 Redirect → /requirements/<id>/)
        ▼
Kullanıcı Sonuç Sayfasına Yönlendirilir
```

---

## MVC / MVT Organizasyonu

| Katman | Django Karşılığı | Dosya | Sorumluluk |
|--------|-----------------|-------|------------|
| **Model** | Django ORM | `models.py` | Veri yapısı ve veritabanı işlemleri |
| **View (Sunum)** | Template | `templates/` | Kullanıcıya gösterilen HTML |
| **Controller** | View + URL | `views.py`, `urls.py` | İş mantığı koordinasyonu |

---

## RESTful Resource Handling

`Requirement` kaynağı RESTful ilkelere göre yönetilir:

| İşlem | HTTP Metodu | URL | Açıklama |
|-------|-------------|-----|----------|
| Index | GET | `/requirements/` | Tüm gereksinimleri listele |
| New | GET | `/requirements/new/` | Yeni form sayfası |
| Create | POST | `/requirements/new/` | Yeni gereksinim oluştur |
| Show | GET | `/requirements/<id>/` | Gereksinim detayı |

---

## Servis Katmanı Mimarisi

View ile veritabanı arasında bir **servis katmanı** (services.py) bulunur. Bu katman:

1. **BDD Üretici**: Kullanıcı girdisini Given-When-Then formatına dönüştürür.
2. **Gherkin Üretici**: Feature/Scenario yapısında test senaryosu üretir.
3. **QA Doğrulayıcı**: Gereksinim kalitesini kontrol eder.
4. **Story Point Tahmin**: Metin uzunluğuna ve içeriğe göre SP hesaplar.

Bu yapı, gelecekte canlı Gemini API veya LangGraph entegrasyonu için hazır tutulmuştur. Servis fonksiyonları değiştirilerek gerçek AI çıktısıyla doğrudan değiştirilebilir.

---

## Veri Modeli

```
Project (1) ──────── (N) Requirement (1) ──────── (1) AnalysisResult
    │                        │
  name                   raw_text                    bdd_output
  description            status                      gherkin_output
  created_at             created_at                  qa_result
                                                     story_point
                                                     created_at
```

---

## Deployment Mimarisi

```
Kullanıcı Tarayıcısı
        │ HTTPS
        ▼
Render.com CDN/Load Balancer
        │
        ▼
Gunicorn WSGI Server (Render Web Service)
        │
        ▼
Django Application (ai_ra_saas)
        │
        ▼
SQLite (Render Disk / Geçici)
```

**Not**: Production ortamında SQLite yerine PostgreSQL kullanılması önerilir. Render'da PostgreSQL eklentisi ile settings.py güncellenerek geçiş yapılabilir.
