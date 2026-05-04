from __future__ import annotations

import json
import os
import re
from datetime import datetime
from io import BytesIO
from textwrap import wrap
from typing import Dict, List, Literal, Optional, TypedDict
from uuid import uuid4

import requests
from docx import Document
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class AnalysisState(TypedDict, total=False):
    project_name: str
    requirement_text: str
    rag_context: str
    api_key: str
    acceptance_criteria: List[str]
    gherkin_scenarios: List[str]
    story_points: int
    qa_feedback: str
    qa_status: Literal["passed", "needs_review"]


class AnalyzeRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    project_name: str
    requirement_text: str
    rag_collection: str = "default"
    api_key: str = ""


class AnalysisResponse(BaseModel):
    session_id: str
    analysis_id: str
    project_name: str
    acceptance_criteria: List[str]
    gherkin_scenarios: List[str]
    story_points: int
    qa_feedback: str
    qa_status: str
    rag_context_used: str
    generated_at: str


class GithubExportRequest(BaseModel):
    analysis_id: str
    repository: str
    token: str
    file_path: str = "exports/analysis.md"
    branch: str = "main"
    commit_message: str = "Add AI-RA analysis export"


class JiraExportRequest(BaseModel):
    analysis_id: str
    jira_base_url: str
    email: str
    api_token: str
    project_key: str
    issue_type: str = "Task"


app = FastAPI(title="AI-RA Backend", version="2.0.0", description="Stateless AI-Driven Requirements Analyst API")
_chroma_client = None
session_store: Dict[str, Dict[str, dict]] = {}


def _get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        import chromadb

        _chroma_client = chromadb.Client()
    return _chroma_client


def _build_markdown(analysis: dict) -> str:
    lines = [
        f"# AI-RA Analysis - {analysis['project_name']}",
        "",
        f"- Analysis ID: {analysis['analysis_id']}",
        f"- Session ID: {analysis['session_id']}",
        f"- Generated At: {analysis['generated_at']}",
        f"- Story Points: {analysis['story_points']}",
        f"- QA Status: {analysis['qa_status']}",
        "",
        "## Requirement",
        analysis["requirement_text"],
        "",
        "## BDD Acceptance Criteria",
    ]
    lines.extend([f"- {item}" for item in analysis["acceptance_criteria"]])
    lines.append("")
    lines.append("## Gherkin Scenarios")
    for scenario in analysis["gherkin_scenarios"]:
        lines.append("```gherkin")
        lines.append(scenario)
        lines.append("```")
        lines.append("")
    lines.append("## QA Feedback")
    lines.append(analysis["qa_feedback"])
    return "\n".join(lines).strip()


def _estimate_story_points(requirement_text: str) -> int:
    length = len(requirement_text.strip())
    if length < 80:
        return 2
    if length < 180:
        return 3
    if length < 320:
        return 5
    if length < 520:
        return 8
    return 13


def _extract_json_payload(text: str) -> dict:
    cleaned = text.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```json\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if not match:
        match = re.search(r"(\{.*\})", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("Model JSON ciktisi ayrisamadi.")
    return json.loads(match.group(1))


def _build_llm(api_key: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,
    )


def analyst_agent(state: AnalysisState) -> AnalysisState:
    llm = _build_llm(state["api_key"])
    requirement_text = state["requirement_text"].strip()
    rag_context = state.get("rag_context", "")
    prompt = (
        "You are the Analyst Agent of AI-RA.\n"
        "Given project requirement text and optional RAG context, produce strict JSON only.\n"
        "Return keys exactly: acceptance_criteria (array of 3-7 BDD Given/When/Then bullets), "
        "gherkin_scenarios (array with 1-3 full valid Gherkin scenario blocks), "
        "story_points (integer from Fibonacci set: 1,2,3,5,8,13).\n"
        "Be specific, testable, and avoid hallucinations.\n\n"
        f"Project Name:\n{state['project_name']}\n\n"
        f"Requirement:\n{requirement_text}\n\n"
        f"RAG Context:\n{rag_context or 'No additional context'}\n"
    )
    response = llm.invoke(prompt)
    data = _extract_json_payload(response.content if isinstance(response.content, str) else str(response.content))
    story_points = int(data.get("story_points", _estimate_story_points(requirement_text)))
    if story_points not in {1, 2, 3, 5, 8, 13}:
        story_points = _estimate_story_points(requirement_text)
    return {
        "acceptance_criteria": data.get("acceptance_criteria", []),
        "gherkin_scenarios": data.get("gherkin_scenarios", []),
        "story_points": story_points,
    }


def qa_agent(state: AnalysisState) -> AnalysisState:
    llm = _build_llm(state["api_key"])
    prompt = (
        "You are the QA Agent of AI-RA.\n"
        "Evaluate the analyst output for consistency, ambiguity, and hallucination risk.\n"
        "Respond in strict JSON only with keys: qa_status (passed|needs_review), qa_feedback (string).\n\n"
        f"Requirement:\n{state['requirement_text']}\n\n"
        f"BDD Acceptance Criteria:\n{json.dumps(state.get('acceptance_criteria', []), ensure_ascii=False)}\n\n"
        f"Gherkin Scenarios:\n{json.dumps(state.get('gherkin_scenarios', []), ensure_ascii=False)}\n\n"
        f"Story Points:\n{state.get('story_points')}\n"
    )
    response = llm.invoke(prompt)
    data = _extract_json_payload(response.content if isinstance(response.content, str) else str(response.content))
    status = data.get("qa_status", "needs_review")
    if status not in {"passed", "needs_review"}:
        status = "needs_review"
    return {"qa_status": status, "qa_feedback": str(data.get("qa_feedback", "QA degerlendirmesi alinamadi."))}


graph = StateGraph(AnalysisState)
graph.add_node("analyst_agent", analyst_agent)
graph.add_node("qa_agent", qa_agent)
graph.set_entry_point("analyst_agent")
graph.add_edge("analyst_agent", "qa_agent")
graph.add_edge("qa_agent", END)
analysis_workflow = graph.compile()


def _fetch_rag_context(collection_name: str, query_text: str) -> str:
    collection = _get_chroma_client().get_or_create_collection(name=collection_name)
    if collection.count() == 0:
        return ""
    query = collection.query(query_texts=[query_text], n_results=3)
    docs = query.get("documents", [[]])[0]
    return "\n".join(docs).strip()


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok", "mode": "stateless-export-only"}


@app.post("/rag/upload", tags=["rag"])
async def upload_rag_pdf(
    session_id: str,
    collection_name: str = "default",
    file: UploadFile = File(...),
) -> dict:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Sadece PDF yuklenebilir.")
    reader = PdfReader(BytesIO(await file.read()))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n".join([page for page in pages if page])
    if not text:
        raise HTTPException(status_code=400, detail="PDF icinde okunabilir metin bulunamadi.")

    chunks = [text[i : i + 900] for i in range(0, len(text), 900)]
    collection = _get_chroma_client().get_or_create_collection(name=collection_name)
    ids = [f"{session_id}-{uuid4()}" for _ in chunks]
    metadatas = [{"session_id": session_id, "source": file.filename}] * len(chunks)
    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    return {"status": "indexed", "chunks_added": len(chunks), "collection_name": collection_name}


@app.post("/analyze", response_model=AnalysisResponse, tags=["analysis"])
def analyze_requirement(request: AnalyzeRequest) -> AnalysisResponse:
    rag_context = _fetch_rag_context(request.rag_collection, request.requirement_text)
    api_key = (
        request.api_key.strip()
        or os.environ.get("TEST_GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
        or os.environ.get("GEMINI_API_KEY", "").strip()
    )
    if not api_key:
        raise HTTPException(status_code=400, detail="API key zorunludur.")
    try:
        result = analysis_workflow.invoke(
            {
                "project_name": request.project_name,
                "requirement_text": request.requirement_text,
                "rag_context": rag_context,
                "api_key": api_key,
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM analizi basarisiz: {exc}") from exc
    analysis_id = str(uuid4())
    payload = {
        "session_id": request.session_id,
        "analysis_id": analysis_id,
        "project_name": request.project_name,
        "requirement_text": request.requirement_text,
        "acceptance_criteria": result["acceptance_criteria"],
        "gherkin_scenarios": result["gherkin_scenarios"],
        "story_points": result["story_points"],
        "qa_feedback": result["qa_feedback"],
        "qa_status": result["qa_status"],
        "rag_context_used": rag_context,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    session_store.setdefault(request.session_id, {})[analysis_id] = payload
    return AnalysisResponse(**payload)


@app.get("/analysis/{session_id}/{analysis_id}", tags=["analysis"])
def get_analysis(session_id: str, analysis_id: str) -> dict:
    analysis = session_store.get(session_id, {}).get(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadi.")
    return analysis


@app.get("/export/pdf/{session_id}/{analysis_id}", tags=["export"])
def export_pdf(session_id: str, analysis_id: str):
    analysis = session_store.get(session_id, {}).get(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadi.")
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    text_obj = pdf.beginText(40, 800)
    for line in _build_markdown(analysis).splitlines():
        for wrapped in wrap(line, 100) or [""]:
            text_obj.textLine(wrapped)
    pdf.drawText(text_obj)
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=analysis-{analysis_id}.pdf"},
    )


@app.get("/export/word/{session_id}/{analysis_id}", tags=["export"])
def export_word(session_id: str, analysis_id: str):
    analysis = session_store.get(session_id, {}).get(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadi.")
    doc = Document()
    doc.add_heading(f"AI-RA Analysis - {analysis['project_name']}", 1)
    doc.add_paragraph(f"Analysis ID: {analysis_id}")
    doc.add_paragraph(f"Story Points: {analysis['story_points']}")
    doc.add_heading("BDD Acceptance Criteria", level=2)
    for item in analysis["acceptance_criteria"]:
        doc.add_paragraph(item, style="List Bullet")
    doc.add_heading("Gherkin Scenarios", level=2)
    for scenario in analysis["gherkin_scenarios"]:
        doc.add_paragraph(scenario)
    doc.add_heading("QA Feedback", level=2)
    doc.add_paragraph(analysis["qa_feedback"])
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=analysis-{analysis_id}.docx"},
    )


@app.post("/export/github/{session_id}", tags=["export"])
def export_to_github(session_id: str, request: GithubExportRequest) -> dict:
    analysis = session_store.get(session_id, {}).get(request.analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadi.")
    api_url = f"https://api.github.com/repos/{request.repository}/contents/{request.file_path}"
    content = _build_markdown(analysis).encode("utf-8")
    payload = {
        "message": request.commit_message,
        "content": __import__("base64").b64encode(content).decode("utf-8"),
        "branch": request.branch,
    }
    headers = {"Authorization": f"Bearer {request.token}", "Accept": "application/vnd.github+json"}
    response = requests.put(api_url, json=payload, headers=headers, timeout=15)
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=400, detail=f"GitHub export hatasi: {response.text}")
    return {"status": "ok", "target": request.repository, "path": request.file_path}


@app.post("/export/jira/{session_id}", tags=["export"])
def export_to_jira(session_id: str, request: JiraExportRequest) -> dict:
    analysis = session_store.get(session_id, {}).get(request.analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadi.")
    issue_url = f"{request.jira_base_url.rstrip('/')}/rest/api/3/issue"
    markdown = _build_markdown(analysis)
    payload = {
        "fields": {
            "project": {"key": request.project_key},
            "summary": f"AI-RA Analysis {request.analysis_id}",
            "issuetype": {"name": request.issue_type},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": markdown[:32767]}],
                    }
                ],
            },
        }
    }
    response = requests.post(issue_url, json=payload, auth=(request.email, request.api_token), timeout=15)
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=400, detail=f"Jira export hatasi: {response.text}")
    data = response.json()
    return {"status": "ok", "jira_issue_key": data.get("key")}
