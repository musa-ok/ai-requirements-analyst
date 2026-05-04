"""
Gereksinim analizi servis katmani.
Cikti uretimi yalnizca Gemini (LangGraph) ile yapilir; sabit/mock metin kullanilmaz.
"""

from __future__ import annotations

import os


def estimate_story_points(raw_text: str) -> int:
    """Gereksinim karmaşıklığına göre story point tahmini yapar (yardımcı fonksiyon)."""
    text = raw_text.strip()
    length = len(text)

    if length < 50:
        return 1
    elif length < 120:
        return 2
    elif length < 250:
        return 3
    elif length < 500:
        return 5
    else:
        return 8


def _resolve_gemini_api_key() -> str:
    return (
        os.environ.get("GOOGLE_API_KEY", "").strip()
        or os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("TEST_GEMINI_API_KEY", "").strip()
    )


def analyze_requirement(raw_text: str, *, project_name: str = "Web Projesi") -> dict:
    """Gemini tabanli analiz; sonuclar tamamen modele baglidir."""
    api_key = _resolve_gemini_api_key()
    if not api_key:
        raise ValueError(
            "Gemini API anahtari bulunamadi. Ortam degiskeni olarak GOOGLE_API_KEY, "
            "GEMINI_API_KEY veya TEST_GEMINI_API_KEY tanimlayin."
        )

    from backend.main import analysis_workflow

    text = raw_text.strip()
    result = analysis_workflow.invoke(
        {
            "project_name": project_name.strip() or "Web Projesi",
            "requirement_text": text,
            "rag_context": "",
            "api_key": api_key,
        }
    )

    bdd_lines = "\n".join(f"- {item}" for item in result["acceptance_criteria"])
    bdd_output = bdd_lines
    gherkin_output = "\n\n".join(result["gherkin_scenarios"])
    qa_result = f"[{result['qa_status']}] {result['qa_feedback']}"

    return {
        "bdd_output": bdd_output,
        "gherkin_output": gherkin_output,
        "qa_result": qa_result,
        "qa_valid": result["qa_status"] == "passed",
        "story_point": result["story_points"],
    }
