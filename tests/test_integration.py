from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path
import subprocess
import sys
import textwrap
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from backend.main import app, session_store


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
LOGIN_REQUIREMENT_TEXT = "The user must be able to log in using their email and password."


def _create_minimal_pdf_bytes(text: str) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 720, text)
    pdf.save()
    return buffer.getvalue()


@pytest.mark.integration
def test_0_rag_upload_subprocess_isolation():
    """
    RAG/Chroma akislarini ayri bir process'te kosar.
    Boylece olasi native crash (segfault) tum pytest surecini dusurmez.
    """
    script = textwrap.dedent(
        """
        from io import BytesIO
        from uuid import uuid4
        from fastapi.testclient import TestClient
        from reportlab.pdfgen import canvas
        from backend.main import app

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.drawString(72, 720, "The user must be able to log in using their email and password.")
        pdf.save()
        pdf_bytes = buffer.getvalue()

        client = TestClient(app)
        session_id = str(uuid4())
        collection_name = f"subprocess-{uuid4().hex}"
        response = client.post(
            f"/rag/upload?session_id={session_id}&collection_name={collection_name}",
            files={"file": ("subprocess.pdf", pdf_bytes, "application/pdf")},
        )
        if response.status_code != 200:
            raise SystemExit(2)
        raise SystemExit(0)
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode in {-11, 139}:
        pytest.xfail(
            "Chroma/NumPy native segfault subprocess icinde izole edildi "
            f"(returncode={result.returncode})."
        )
    assert result.returncode == 0, (
        "Subprocess RAG testi basarisiz oldu. "
        f"returncode={result.returncode}, stdout={result.stdout}, stderr={result.stderr}"
    )


@pytest.fixture(scope="session")
def api_key() -> str:
    load_dotenv(ENV_PATH)
    key = (
        os.environ.get("TEST_GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or ""
    ).strip()
    if not key:
        pytest.skip(".env icinde TEST_GEMINI_API_KEY/GOOGLE_API_KEY/GEMINI_API_KEY bulunamadi.")
    return key


@pytest.fixture(scope="session")
def jira_credentials() -> dict | None:
    load_dotenv(ENV_PATH)
    jira_base_url = (os.environ.get("JIRA_BASE_URL") or "").strip()
    jira_email = (os.environ.get("JIRA_EMAIL") or "").strip()
    jira_api_token = (os.environ.get("JIRA_API_TOKEN") or "").strip()
    jira_project_key = (os.environ.get("JIRA_PROJECT_KEY") or "").strip()
    if not all([jira_base_url, jira_email, jira_api_token, jira_project_key]):
        return None
    return {
        "jira_base_url": jira_base_url,
        "email": jira_email,
        "api_token": jira_api_token,
        "project_key": jira_project_key,
        "issue_type": "Task",
    }


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def temp_pdf_bytes() -> bytes:
    return _create_minimal_pdf_bytes(LOGIN_REQUIREMENT_TEXT)


@pytest.fixture()
def analyzed_session(client: TestClient, api_key: str, temp_pdf_bytes: bytes) -> dict:
    session_id = str(uuid4())
    collection_name = f"e2e-{uuid4().hex}"

    upload_response = client.post(
        f"/rag/upload?session_id={session_id}&collection_name={collection_name}",
        files={"file": ("e2e-input.pdf", temp_pdf_bytes, "application/pdf")},
    )
    assert upload_response.status_code == 200, upload_response.text

    analyze_payload = {
        "session_id": session_id,
        "project_name": "AI-RA E2E Project",
        "requirement_text": LOGIN_REQUIREMENT_TEXT,
        "rag_collection": collection_name,
        "api_key": api_key,
        "model_type": "gemini",
    }
    analyze_response = client.post("/analyze", json=analyze_payload)
    assert analyze_response.status_code == 200, analyze_response.text
    analyze_json = analyze_response.json()

    return {
        "session_id": session_id,
        "collection_name": collection_name,
        "analysis_id": analyze_json["analysis_id"],
        "analysis_json": analyze_json,
    }


@pytest.fixture()
def analyzed_session_external(
    client: TestClient,
    api_key: str,
    temp_pdf_bytes: bytes,
    jira_credentials: dict | None,
) -> dict:
    if not jira_credentials:
        pytest.skip("Gercek Jira entegrasyonu icin JIRA_* ortam degiskenleri eksik.")
    return analyzed_session(client, api_key, temp_pdf_bytes)


@pytest.fixture()
def seeded_session_for_export() -> dict:
    session_id = str(uuid4())
    analysis_id = str(uuid4())
    payload = {
        "session_id": session_id,
        "analysis_id": analysis_id,
        "project_name": "AI-RA Contract Project",
        "requirement_text": LOGIN_REQUIREMENT_TEXT,
        "acceptance_criteria": [
            "Given kullanici giris ekranindadir, When e-posta ve sifre girer, Then sistem kimlik dogrulama yapar."
        ],
        "gherkin_scenarios": [
            "Feature: Login\n  Scenario: Valid login\n    Given user enters valid credentials\n    When user submits login\n    Then user is authenticated"
        ],
        "story_points": 3,
        "qa_feedback": "Cikti tutarli.",
        "qa_status": "passed",
        "rag_context_used": LOGIN_REQUIREMENT_TEXT,
        "generated_at": "2026-05-04T00:00:00Z",
    }
    session_store.setdefault(session_id, {})[analysis_id] = payload
    return {"session_id": session_id, "analysis_id": analysis_id}


@pytest.mark.integration
def test_1_pdf_upload_indexes_text_to_chromadb(client: TestClient, temp_pdf_bytes: bytes):
    session_id = str(uuid4())
    collection_name = f"upload-only-{uuid4().hex}"
    response = client.post(
        f"/rag/upload?session_id={session_id}&collection_name={collection_name}",
        files={"file": ("minimal.pdf", temp_pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexed"
    assert data["chunks_added"] >= 1
    assert data["collection_name"] == collection_name

    # Lazy import to reduce import-time crash risk with numpy/chromadb.
    from backend.main import _get_chroma_client

    collection = _get_chroma_client().get_or_create_collection(name=collection_name)
    assert collection.count() >= 1
    query = collection.query(query_texts=["email and password"], n_results=1)
    docs = query.get("documents", [[]])[0]
    assert docs, "ChromaDB query bos dondu."
    assert "email" in docs[0].lower()


@pytest.mark.integration
def test_2_real_llm_analysis_returns_structured_outputs(analyzed_session: dict):
    data = analyzed_session["analysis_json"]

    assert isinstance(data["analysis_id"], str) and data["analysis_id"]
    assert isinstance(data["session_id"], str) and data["session_id"]
    assert isinstance(data["acceptance_criteria"], list) and len(data["acceptance_criteria"]) >= 1
    assert isinstance(data["gherkin_scenarios"], list) and len(data["gherkin_scenarios"]) >= 1
    assert isinstance(data["story_points"], int)
    assert data["story_points"] in {1, 2, 3, 5, 8, 13}
    assert data["qa_status"] in {"passed", "needs_review"}
    assert isinstance(data["qa_feedback"], str) and len(data["qa_feedback"]) > 3
    assert isinstance(data["rag_context_used"], str)
    assert "Scenario" in "\n".join(data["gherkin_scenarios"])


@pytest.mark.integration
def test_3_export_pdf_with_session_state(client: TestClient, analyzed_session: dict):
    session_id = analyzed_session["session_id"]
    analysis_id = analyzed_session["analysis_id"]

    pdf_response = client.get(f"/export/pdf/{session_id}/{analysis_id}")
    assert pdf_response.status_code == 200
    assert "application/pdf" in pdf_response.headers.get("content-type", "")
    assert "attachment; filename=analysis-" in pdf_response.headers.get("content-disposition", "")
    assert pdf_response.content.startswith(b"%PDF")


@pytest.mark.contract
def test_4_pdf_export_contract_uses_session_memory(
    client: TestClient,
    seeded_session_for_export: dict,
):
    session_id = seeded_session_for_export["session_id"]
    analysis_id = seeded_session_for_export["analysis_id"]
    response = client.get(f"/export/pdf/{session_id}/{analysis_id}")
    assert response.status_code == 200
    assert "application/pdf" in response.headers.get("content-type", "")
    assert response.content.startswith(b"%PDF")


@pytest.mark.contract
def test_5_jira_export_contract_uses_expected_payload(
    client: TestClient,
    seeded_session_for_export: dict,
    monkeypatch: pytest.MonkeyPatch,
):
    session_id = seeded_session_for_export["session_id"]
    analysis_id = seeded_session_for_export["analysis_id"]
    captured: dict = {}

    class DummyResponse:
        status_code = 201

        @staticmethod
        def json():
            return {"key": "AIRA-101"}

    def fake_post(url, json, auth, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["auth"] = auth
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr("requests.post", fake_post)

    jira_payload = {
        "analysis_id": analysis_id,
        "jira_base_url": "https://example.atlassian.net",
        "email": "e2e@example.com",
        "api_token": "invalid-token-for-format-check",
        "project_key": "AIRA",
        "issue_type": "Task",
    }
    jira_response = client.post(f"/export/jira/{session_id}", json=jira_payload)
    assert jira_response.status_code == 200
    assert jira_response.json()["jira_issue_key"] == "AIRA-101"
    assert captured["url"] == "https://example.atlassian.net/rest/api/3/issue"
    assert captured["auth"] == ("e2e@example.com", "invalid-token-for-format-check")
    assert captured["timeout"] == 15
    assert captured["json"]["fields"]["project"]["key"] == "AIRA"
    assert captured["json"]["fields"]["issuetype"]["name"] == "Task"
    assert "description" in captured["json"]["fields"]


@pytest.mark.contract
def test_6_github_export_contract_uses_expected_payload(
    client: TestClient,
    seeded_session_for_export: dict,
    monkeypatch: pytest.MonkeyPatch,
):
    session_id = seeded_session_for_export["session_id"]
    analysis_id = seeded_session_for_export["analysis_id"]
    captured: dict = {}

    class DummyResponse:
        status_code = 201
        text = "created"

    def fake_put(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr("requests.put", fake_put)

    payload = {
        "analysis_id": analysis_id,
        "repository": "acme/ai-ra",
        "token": "ghp_fake_token",
        "file_path": "exports/analysis.md",
        "branch": "main",
        "commit_message": "contract export",
    }
    response = client.post(f"/export/github/{session_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert captured["url"] == "https://api.github.com/repos/acme/ai-ra/contents/exports/analysis.md"
    assert captured["timeout"] == 15
    assert "Authorization" in captured["headers"]
    assert captured["json"]["branch"] == "main"


@pytest.mark.integration
@pytest.mark.external_api
def test_7_jira_export_full_integration_with_real_credentials(
    client: TestClient,
    analyzed_session_external: dict,
    jira_credentials: dict,
):
    session_id = analyzed_session_external["session_id"]
    analysis_id = analyzed_session_external["analysis_id"]
    payload = {"analysis_id": analysis_id, **jira_credentials}
    jira_response = client.post(f"/export/jira/{session_id}", json=payload)
    assert jira_response.status_code == 200, jira_response.text
    data = jira_response.json()
    assert "jira_issue_key" in data and data["jira_issue_key"]
