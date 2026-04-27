# AI-RA: AI-Driven Requirements Analyst 🚀

AI-RA is a state-of-the-art **Multi-Agent Requirements Analysis System** designed to bridge the gap between vague software ideas and structured, testable engineering specifications.

Built with **Multi-Agent Orchestration** logic using **LangGraph**, it ensures high-quality output by simulating a collaborative environment between an Analyst Agent and a QA Agent.

---

## ✨ Key Features

- **Modern Dark UI v2:** A sleek, minimalist dashboard with neon-cyan micro-interactions.
- **Multi-Agent Workflow:** Autonomous agents (Analyst & QA) work together to refine requirements and eliminate hallucinations.
- **Corporate Memory (RAG):** Context-aware analysis utilizing uploaded PDF/Word documents to match corporate standards.
- **Smart Output:** Automatically generates **Gherkin Scenarios**, **BDD Acceptance Criteria**, and **Story Point Estimates**.
- **Developer UX:** Power-user features like `Cmd+Enter` shortcuts and real-time shimmer loading states.

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python 3.9.6, FastAPI, LangGraph |
| **LLM** | Google Gemini 2.5 Flash |
| **Database** | PostgreSQL & ChromaDB (Vector Store) |
| **Frontend** | Vanilla JavaScript, Modern CSS3 (Dark Aesthetic) |


---

## 👥 The Squad (Team)

| Role | Name |
| :--- | :--- |
| **Project Leader** | **Muhammed Sina Gün** |
| **Tester** | **Berk Kızgın** |
| **Developer** | **Musa Ok** |
| **Developer** | **Seyyid Muhammed Sun** |
| **Developer** | **Şahin Kara** |

---

## 🎓 Academic Context

This project is developed as part of the **BLML210 Software Engineering** course at **Istanbul Arel University**.

**Supervisor:** Professor Haluk Gümüşkaya

---

## 📁 Project Structure

```text
ai-requirements-analyzer/
├── backend/
│   ├── main.py
│   ├── core/
│   └── rag/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── data/
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1) Clone the repository

```bash
git clone https://github.com/your-username/ai-requirements-analyzer.git
cd ai-requirements-analyzer
```

### 2) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Configure environment variables

Create or edit `.env`:

```env
GOOGLE_API_KEY=your_google_api_key_here
CHROMA_DB_PATH=./data/chroma
```

### 5) Run backend API

```bash
uvicorn backend.main:app --reload
```

Backend health endpoint:

```text
http://127.0.0.1:8000/health
```

### 6) Run frontend

Open `frontend/index.html` directly in your browser, or serve it with a lightweight static server:

```bash
python3 -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500/frontend/
```

---

## 🔭 Roadmap

- Integrate full Analyst/QA LangGraph node orchestration in `backend/core`.
- Add document ingestion and retrieval flow under `backend/rag`.
- Add PostgreSQL persistence for projects, outputs, and revision history.
- Add Jira export and PDF generation backend endpoints.

---

## 📄 License

This project is currently maintained for academic and demonstration purposes.
