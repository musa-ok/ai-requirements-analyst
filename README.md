# AI-RA: AI-Driven Requirements Analyst

AI-RA is a **Multi-Agent Requirements Analysis System** that transforms vague software ideas into structured, testable engineering specifications.

---

## HW5 — FirstSaaSPrototype (Django)

The `FirstSaaSPrototype` in this repo is the HW5 submission: a working Django MVT SaaS prototype demonstrating 3-tier architecture, RESTful routing, BDD/Gherkin output generation, and full test coverage.

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/requirements/new/` | Requirement input form |
| `/requirements/<id>/` | Analysis result page |
| `/requirements/` | History list |

**Run locally:**
```bash
python -m venv venv
venv\Scripts\activate
pip install Django gunicorn whitenoise pytest pytest-django behave
python manage.py migrate
python manage.py runserver
```

**Tests:** `python manage.py test` → 44/44 passing

**Deploy:** Render.com — `gunicorn ai_ra_saas.wsgi`

---

## AI Core (FastAPI + LangGraph)

The main AI backend uses FastAPI, LangGraph, and Google Gemini for multi-agent requirement analysis.

**Tech Stack:**

| Layer | Technology |
|:---|:---|
| **Backend** | Python, FastAPI, LangGraph |
| **LLM** | Google Gemini 2.5 Flash |
| **Database** | PostgreSQL & ChromaDB (Vector Store) |
| **Frontend** | Vanilla JavaScript, Modern CSS3 |

**Run backend:**
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

---

## Team

| Role | Name |
|:---|:---|
| **Project Leader** | Muhammed Sina Gün |
| **Tester** | Berk Kızgın |
| **Developer** | Musa Ok |
| **Developer** | Seyyid Muhammed Sun |
| **Developer** | Şahin Kara |

**Supervisor:** Prof. Dr. Haluk Gümüşkaya — Istanbul Arel University, BLML210 Software Engineering
