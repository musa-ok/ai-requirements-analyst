"""Django analiz sonucunu FastAPI session_store'a kaydeder (export icin)."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import uuid4


def ensure_fastapi_session_id(request) -> str:
    key = "ai_ra_fastapi_session_id"
    session_id = request.session.get(key)
    if not session_id:
        session_id = str(uuid4())
        request.session[key] = session_id
        request.session.modified = True
    return session_id


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
        or "http://127.0.0.1:8001"
    ).rstrip("/")


def _register_in_process(api_session_id: str, payload: dict) -> str:
    from backend.main import session_store

    analysis_id = str(uuid4())
    record = {
        **payload,
        "session_id": api_session_id,
        "analysis_id": analysis_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    session_store.setdefault(api_session_id, {})[analysis_id] = record
    return analysis_id


def register_analysis_for_export(
    *,
    api_session_id: str,
    project_name: str,
    requirement_text: str,
    acceptance_criteria: List[str],
    gherkin_scenarios: List[str],
    story_points: int,
    qa_feedback: str,
    qa_status: str,
    rag_context_used: str = "",
) -> Optional[str]:
    """FastAPI'ye HTTP ile kayit dener; basarisizsa ayni process icinde dener."""
    body = {
        "session_id": api_session_id,
        "project_name": project_name,
        "requirement_text": requirement_text,
        "acceptance_criteria": acceptance_criteria,
        "gherkin_scenarios": gherkin_scenarios,
        "story_points": story_points,
        "qa_feedback": qa_feedback,
        "qa_status": qa_status,
        "rag_context_used": rag_context_used,
    }
    base = _fastapi_base_url()
    if base and base not in ("inprocess", "memory"):
        try:
            import requests

            response = requests.post(f"{base}/analysis/register", json=body, timeout=15)
            if response.status_code == 200:
                return response.json().get("analysis_id")
        except Exception:
            pass
    try:
        return _register_in_process(api_session_id, body)
    except Exception:
        return None


def _format_analysis_for_display(api_payload: dict) -> dict:
    """FastAPI kaydini Django sablon alanlarina donusturur."""
    criteria = api_payload.get("acceptance_criteria") or []
    bdd_output = "\n".join(f"- {item}" for item in criteria)
    gherkin_output = "\n\n".join(api_payload.get("gherkin_scenarios") or [])
    qa_status = api_payload.get("qa_status") or "needs_review"
    qa_label = "Onaylandi" if qa_status == "passed" else "Inceleme gerekli"
    qa_feedback = api_payload.get("qa_feedback") or ""
    return {
        "bdd_output": bdd_output,
        "gherkin_output": gherkin_output,
        "qa_result": f"[{qa_label}] {qa_feedback}",
        "story_point": int(api_payload.get("story_points") or 0),
    }


def fetch_analysis_from_api(api_session_id: str, analysis_id: str) -> Optional[dict]:
    """Kayitli analizi FastAPI'den okur (HTTP veya ayni process)."""
    base = _fastapi_base_url()
    if base and base not in ("inprocess", "memory"):
        try:
            import requests

            response = requests.get(
                f"{base}/analysis/{api_session_id}/{analysis_id}",
                timeout=15,
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
    try:
        from backend.main import session_store

        return session_store.get(api_session_id, {}).get(analysis_id)
    except Exception:
        return None


def register_from_analysis_result(
    request,
    *,
    project_name: str,
    requirement_text: str,
    analysis: dict,
) -> Tuple[str, Optional[str]]:
    api_session_id = ensure_fastapi_session_id(request)
    analysis_id = register_analysis_for_export(
        api_session_id=api_session_id,
        project_name=project_name,
        requirement_text=requirement_text,
        acceptance_criteria=analysis.get("acceptance_criteria") or [],
        gherkin_scenarios=analysis.get("gherkin_scenarios") or [],
        story_points=int(analysis.get("story_points") or analysis.get("story_point") or 0),
        qa_feedback=analysis.get("qa_feedback") or "",
        qa_status=analysis.get("qa_status") or "needs_review",
    )
    return api_session_id, analysis_id
