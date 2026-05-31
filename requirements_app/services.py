"""
Gereksinim analizi servis katmani.
Cikti uretimi yalnizca Gemini (LangGraph) ile yapilir; sabit/mock metin kullanilmaz.
"""

from __future__ import annotations


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


def analyze_requirement(
    raw_text: str,
    *,
    project_name: str = "Web Projesi",
    api_key: str,
    model_type: str = "gemini",
) -> dict:
    """Gemini tabanli analiz; anahtar istemciden gelir, sunucu ortam degiskeni kullanilmaz."""
    key = (api_key or "").strip()
    if not key:
        raise ValueError(
            "API anahtari zorunludur. Analiz icin Gemini API anahtarini formda veya istekle gonderin."
        )

    from backend.main import get_analysis_workflow

    text = raw_text.strip()
    result = get_analysis_workflow().invoke(
        {
            "project_name": project_name.strip() or "Web Projesi",
            "requirement_text": text,
            "rag_context": "",
            "api_key": key,
            "model_type": (model_type or "gemini").strip().lower() or "gemini",
        }
    )

    bdd_lines = "\n".join(f"- {item}" for item in result["acceptance_criteria"])
    bdd_output = bdd_lines
    gherkin_output = "\n\n".join(result["gherkin_scenarios"])
    qa_status = result["qa_status"]
    qa_label = "Onaylandi" if qa_status == "passed" else "Inceleme gerekli"
    qa_result = f"[{qa_label}] {result['qa_feedback']}"

    return {
        "bdd_output": bdd_output,
        "gherkin_output": gherkin_output,
        "qa_result": qa_result,
        "qa_valid": result["qa_status"] == "passed",
        "story_point": result["story_points"],
        "acceptance_criteria": result["acceptance_criteria"],
        "gherkin_scenarios": result["gherkin_scenarios"],
        "story_points": result["story_points"],
        "qa_feedback": result["qa_feedback"],
        "qa_status": result["qa_status"],
    }
