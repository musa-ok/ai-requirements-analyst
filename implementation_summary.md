# Implementation Summary — AI_RA

## Güncel mimari (2026)

- **Django UI**: Form → `services.analyze_requirement()` → LangGraph (in-process) → signed-cookie session
- **FastAPI**: REST `/analyze`, `/analysis/register`, export uçları, lazy LangChain boot
- **SPA** (`frontend/`): FastAPI’ye HTTP; tam export/RAG/çoklu model

Analiz sonuçları **SQLite ORM’a yazılmaz** (`models.py` boş; session-only).

## Teknolojiler

- Django 4.2, SQLite, WhiteNoise, Gunicorn
- FastAPI, LangGraph, langchain-google-genai / anthropic / openai
- ChromaDB (bellek veya `CHROMA_PERSIST_DIR`)
- pytest, pytest-django, behave, GitHub Actions CI

## Servis katmanı (`requirements_app/services.py`)

| Fonksiyon | Açıklama |
|-----------|----------|
| `analyze_requirement(..., api_key, model_type)` | LangGraph analiz; LLM çıktısı |
| `estimate_story_points(text)` | Yardımcı Fibonacci tahmini (LLM dışı) |

## Export köprüsü (`requirements_app/export_bridge.py`)

Django analiz sonrası FastAPI `session_store`’a kayıt (`POST /analysis/register` veya in-process fallback) — PDF/Word/Jira/GitHub export için.

## Sayfalar

1. `/` — Ana sayfa  
2. `/requirements/new/` — Analiz formu (+ API key, Ayarlardan otomatik doldurma)  
3. `/requirements/<id>/` — Sonuç + Markdown/PDF/Word/Jira/GitHub export  
4. `/requirements/` — Geçmiş liste  

Detaylı durum: `STATUS.md`
