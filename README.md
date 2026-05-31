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
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Tests:** `python -m pytest` + `python manage.py test requirements_app`

**Deploy:** DigitalOcean — bkz. `DEPLOYMENT_DO.md`

---

## AI Core (FastAPI + LangGraph)

The main AI backend uses FastAPI, LangGraph, and Google Gemini for multi-agent requirement analysis.

**Tech Stack:**

| Layer | Technology |
|:---|:---|
| **Backend** | Python, FastAPI, LangGraph |
| **LLM** | Google Gemini 2.5 Flash |
| **Persistence** | Django: signed-cookie session · FastAPI: in-memory + opsiyonel Chroma disk |
| **Vector store** | ChromaDB (in-process; `CHROMA_PERSIST_DIR` ile kalıcı) |
| **Frontend** | Vanilla JavaScript, Modern CSS3 |

**Run backend:**
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
```

**Run SPA (ayri terminal):**
```bash
cd frontend && python3 -m http.server 5500
# Tarayici: http://127.0.0.1:5500 — Ayarlarda backend URL: http://127.0.0.1:8001
```

**Tests:** `python -m pytest` (Django + FastAPI contract + health)

| Role | Name |
|:---|:---|
| **Project Leader** | Muhammed Sina Gün |
| **Tester** | Berk Kızgın |
| **Developer** | Musa Ok |
| **Developer** | Seyyid Muhammed Sun |
| **Developer** | Şahin Kara |

**Supervisor:** Prof. Dr. Haluk Gümüşkaya — Istanbul Arel University, BLML210 Software Engineering
