"""Gereksinim analizi servis katmani."""

from __future__ import annotations

import os
from uuid import uuid4


def _format_llm_error(exc: Exception) -> str:
    """LLM/SDK hatalarini kullaniciya anlasilir Turkce mesaja cevirir."""
    name = type(exc).__name__
    text = str(exc).lower()
    if name == "ResourceExhausted" or "429" in str(exc) or "quota" in text or "rate" in text:
        return (
            "Gemini API kotasi doldu (ucretsiz planda gemini-2.5-flash ~20 istek/gun). "
            "Bir dakika bekleyip tekrar deneyin, Google AI Studio'da faturalandirma acin "
            "veya baska bir API anahtari/model kullanin."
        )
    if "api key" in text or "api_key" in text or "invalid" in text and "key" in text:
        return "API anahtari gecersiz veya reddedildi. Ayarlardan yeni bir anahtar girin."
    if "permission" in text or "403" in str(exc):
        return "API anahtarinin bu modele erisim izni yok."
    if "timeout" in text or "timed out" in text:
        return "Analiz zaman asimina ugradi. Tekrar deneyin veya API servisini kontrol edin."
    return "Analiz sirasinda yapay zeka servisi hatasi olustu. Lutfen tekrar deneyin."


def _fastapi_base_url() -> str:
    try:
        from django.conf import settings

        configured = getattr(settings, "FASTAPI_BASE_URL", "").strip()
        if configured:
            return configured.rstrip("/")
    except Exception:
        pass
    return (
        os.environ.get("FASTAPI_BASE_URL", "").strip()
        or os.environ.get("AI_RA_API_BASE_URL", "").strip()
    ).rstrip("/")


def _use_http_analyze() -> bool:
    base = _fastapi_base_url()
    return bool(base) and base not in ("inprocess", "memory")


def _result_from_workflow(result: dict) -> dict:
    bdd_lines = "\n".join(f"- {item}" for item in result["acceptance_criteria"])
    gherkin_output = "\n\n".join(result["gherkin_scenarios"])
    qa_status = result["qa_status"]
    qa_label = "Onaylandi" if qa_status == "passed" else "Inceleme gerekli"
    qa_result = f"[{qa_label}] {result['qa_feedback']}"
    return {
        "bdd_output": bdd_lines,
        "gherkin_output": gherkin_output,
        "qa_result": qa_result,
        "qa_valid": qa_status == "passed",
        "story_point": result["story_points"],
        "acceptance_criteria": result["acceptance_criteria"],
        "gherkin_scenarios": result["gherkin_scenarios"],
        "story_points": result["story_points"],
        "qa_feedback": result["qa_feedback"],
        "qa_status": qa_status,
    }


def _analyze_via_http(
    *,
    raw_text: str,
    project_name: str,
    api_key: str,
    model_type: str,
) -> dict:
    import requests

    base = _fastapi_base_url()
    if not base:
        raise ValueError("FASTAPI_BASE_URL tanimli degil; analiz API servisine yonlendirilemedi.")

    body = {
        "session_id": str(uuid4()),
        "project_name": project_name.strip() or "Web Projesi",
        "requirement_text": raw_text.strip(),
        "rag_collection": "default",
        "api_key": api_key,
        "model_type": (model_type or "gemini").strip().lower() or "gemini",
    }
    try:
        response = requests.post(f"{base}/analyze", json=body, timeout=170)
    except requests.Timeout as exc:
        raise ValueError(_format_llm_error(exc)) from exc
    except requests.RequestException as exc:
        raise ValueError(
            "Analiz API servisine ulasilamadi. FASTAPI_BASE_URL ve api servisinin calistigini kontrol edin."
        ) from exc

    if response.status_code >= 400:
        detail = response.text
        try:
            payload = response.json()
            detail = payload.get("detail", detail)
            if isinstance(detail, list):
                detail = "; ".join(str(item) for item in detail)
        except Exception:
            pass
        raise ValueError(_format_llm_error(Exception(str(detail))))

    data = response.json()
    return _result_from_workflow(
        {
            "acceptance_criteria": data.get("acceptance_criteria") or [],
            "gherkin_scenarios": data.get("gherkin_scenarios") or [],
            "story_points": int(data.get("story_points") or 0),
            "qa_feedback": data.get("qa_feedback") or "",
            "qa_status": data.get("qa_status") or "needs_review",
        }
    )


def _analyze_in_process(
    *,
    raw_text: str,
    project_name: str,
    api_key: str,
    model_type: str,
) -> dict:
    from backend.main import get_analysis_workflow

    result = get_analysis_workflow().invoke(
        {
            "project_name": project_name.strip() or "Web Projesi",
            "requirement_text": raw_text.strip(),
            "rag_context": "",
            "api_key": api_key,
            "model_type": (model_type or "gemini").strip().lower() or "gemini",
        }
    )
    return _result_from_workflow(result)


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
    """Analiz: FASTAPI_BASE_URL varsa HTTP, yoksa lokal in-process."""
    key = (api_key or "").strip()
    if not key:
        raise ValueError(
            "API anahtari zorunludur. Analiz icin Gemini API anahtarini formda veya istekle gonderin."
        )

    try:
        if _use_http_analyze():
            return _analyze_via_http(
                raw_text=raw_text,
                project_name=project_name,
                api_key=key,
                model_type=model_type,
            )
        return _analyze_in_process(
            raw_text=raw_text,
            project_name=project_name,
            api_key=key,
            model_type=model_type,
        )
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(_format_llm_error(exc)) from exc
