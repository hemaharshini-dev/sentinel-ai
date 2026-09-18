# Sentinel AI

Sentinel AI is a prototype fraud-analysis project that reads a suspicious complaint, extracts scam-related entities, checks for similar complaints, and produces a structured report. It is currently implemented as a FastAPI backend, a LangGraph workflow, and a lightweight React + Vite frontend.

## Current status

This project is a working MVP/prototype rather than a production-grade fraud platform. The current implementation focuses on:

- analyzing a complaint message using an LLM
- extracting structured entities such as phone numbers, UPI IDs, emails, URLs, amounts, authorities, and Telegram IDs
- saving complaints to a local JSON dataset
- finding related complaints by shared entity values
- returning a final intelligence summary in JSON
- showing the result in a simple UI dashboard

## What is implemented

### Backend

The backend in [backend/main.py](backend/main.py) exposes a small API:

- `GET /` — health check endpoint
- `POST /analyze` — accepts a complaint message and runs the analysis workflow
- `POST /crisis` — accepts a previous analysis plus a user reply and returns a crisis-safe response JSON

The backend uses:

- FastAPI
- Pydantic models
- Groq via `langchain_groq`
- LangGraph workflow orchestration
- NetworkX for graph-based complaint matching

### LangGraph workflow

The analysis pipeline is defined in [backend/graph/workflow.py](backend/graph/workflow.py) and runs these steps:

1. Investigation agent
2. Entity extraction agent
3. Graph persistence step
4. Campaign intelligence step
5. Final report generation

The actual node definitions are in [backend/graph/nodes.py](backend/graph/nodes.py).

### Agents

The project currently includes the following agents:

- [backend/agents/investigation_agent.py](backend/agents/investigation_agent.py)
  - identifies scam type, summary, reason, and immediate actions
- [backend/agents/entity_agent.py](backend/agents/entity_agent.py)
  - extracts entities from the message
- [backend/agents/intelligence_agent.py](backend/agents/intelligence_agent.py)
  - checks for related complaints using shared entities
- [backend/agents/report_agent.py](backend/agents/report_agent.py)
  - builds a final JSON report
- [backend/agents/crisis_agent.py](backend/agents/crisis_agent.py)
  - returns a safety-oriented reply based on a prior analysis and the user message

### Data layer

Complaint records are stored in [backend/data/complaints.json](backend/data/complaints.json).

The graph matching logic is implemented in [backend/graph_db/graph_manager.py](backend/graph_db/graph_manager.py). It:

- loads complaint records from JSON
- builds a NetworkX graph from complaint-to-entity relationships
- finds similar complaints by matching shared entity values

This is a lightweight prototype graph system, not a production database-backed graph service.

### Frontend

The frontend is a React + TypeScript app built with Vite, located in [frontend/src/App.tsx](frontend/src/App.tsx).

It lets the user:

- paste a suspicious complaint
- click Analyze Complaint
- send the text to the backend
- view the investigation, entities, intelligence, and final report in one dashboard

The package scripts are defined in [frontend/package.json](frontend/package.json):

- `npm run dev` — run the Vite dev server
- `npm run build` — build the frontend
- `npm run lint` — lint the app
- `npm run preview` — preview the production build

## Project structure

```text
sentinel-ai/
  backend/
    main.py                    FastAPI app and API routes
    llm.py                     Groq-backed LLM client
    agents/                    analysis agents for investigation, entities, intelligence, reports, and crisis support
    graph/                     LangGraph workflow and state definitions
    graph_db/                  complaint storage and related-match logic
    utils/                     JSON parsing helpers
    data/complaints.json       local complaint dataset used by the app
    test_graph.py              smoke test for the workflow
    test_graph_db.py           smoke test for graph matching
  frontend/
    src/                       React frontend source
    public/                    static assets
    package.json               frontend dependencies and scripts
    vite.config.ts            Vite config
  assets/                     currently empty
  docs/                       currently empty
  README.md                   project overview
```

## How the current flow works

1. The user enters a suspicious message in the frontend.
2. The frontend posts it to the backend at `http://127.0.0.1:8000/analyze`.
3. The backend runs the LangGraph pipeline.
4. The investigation agent assesses the scam.
5. The entity agent extracts structured indicators from the text.
6. The graph step saves the complaint to [backend/data/complaints.json](backend/data/complaints.json).
7. The intelligence step checks related complaints by shared values.
8. The report agent produces a final JSON report.
9. The frontend displays all JSON sections in the dashboard.

## Setup

### 1. Backend

From the project root:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn pydantic python-dotenv langchain-groq langgraph networkx
```

Then make sure a `GROQ_API_KEY` is available in your environment or in a `.env` file inside the backend folder.

Run the backend:

```bash
uvicorn main:app --reload
```

### 2. Frontend

From the project root:

```bash
dcd frontend
npm install
npm run dev
```

Then open the frontend in the browser. The frontend is currently configured to call the backend at `http://127.0.0.1:8000`.

## Important implementation notes

- The backend CORS configuration in [backend/main.py](backend/main.py) currently allows `http://localhost:5173`.
- The frontend is currently hardcoded to call `http://127.0.0.1:8000/analyze` in [frontend/src/App.tsx](frontend/src/App.tsx).
- If you run the frontend on a different host/port, update both the frontend URL and the backend CORS origin to match.
- The complaint dataset in [backend/data/complaints.json](backend/data/complaints.json) is demo/sample data and includes repeated IDs from testing.
- The project uses local JSON persistence and NetworkX instead of a dedicated graph database service.
- The app is still a prototype and is designed for demonstration and experimentation, not production deployment.

## Example input

This prototype is intended for messages like:

- fake government officer scams
- urgent transfer requests
- UPI payment fraud messages
- suspicious emails, URLs, or Telegram IDs
- repeated complaint patterns across multiple victims

## Troubleshooting

- If the frontend cannot connect to the backend, confirm the backend is running with `uvicorn main:app --reload` in the backend folder.
- If the analysis fails, check whether `GROQ_API_KEY` is set correctly.
- If no related complaints are found, that can happen naturally when the dataset is empty or when no entity overlap exists.
- If you see CORS errors, align the frontend URL and backend allowed origin settings.

## Development notes

- [backend/test_graph.py](backend/test_graph.py) is a quick workflow smoke test.
- [backend/test_graph_db.py](backend/test_graph_db.py) tests the matching logic against sample complaints.
- The LLM responses are parsed as JSON, so the prompts are designed to return strict structured output.
- The project currently relies on heuristic entity matching from stored complaint records rather than a full graph database or advanced deduplication engine.
