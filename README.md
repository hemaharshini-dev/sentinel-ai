# Sentinel AI

Sentinel AI is a fraud network intelligence platform that analyzes suspicious cybercrime complaints using a multi-agent LangGraph pipeline. It extracts scam indicators, matches complaints against a historical database, scores risk, generates victim guidance, and provides an interactive crisis companion — all through a React frontend backed by a FastAPI server.

---

## Current Status

Fully working beyond MVP. The pipeline has 8 agents running in sequence, a SQLite complaint database, a rebuilt React UI with structured cards and a crisis chat panel, LangSmith tracing, and multi-language support.

---

## Architecture

### Pipeline (LangGraph)

Every `/analyze` request runs this sequence:

```
Language → Investigation → Entity → Graph → Intelligence → Risk → Guidance → Report
```

| Step | Agent | What it does |
|---|---|---|
| 1 | Language Agent | Detects language, translates to English if needed (Hindi, Tamil, Telugu, etc.) |
| 2 | Investigation Agent | Identifies scam type, writes summary, explains why it's suspicious |
| 3 | Entity Agent | Extracts phone numbers, UPI IDs, emails, URLs, bank accounts, Telegram IDs, amounts |
| 4 | Graph Node | Saves complaint to SQLite with timestamp, scam type, raw message, entities |
| 5 | Intelligence Agent | Matches against historical complaints via NetworkX graph, detects campaigns |
| 6 | Risk Agent | Scores complaint 0–100 using deterministic signals, assigns LOW/MEDIUM/HIGH/CRITICAL |
| 7 | Guidance Agent | Generates scam-specific victim steps, DO NOT list, evidence checklist |
| 8 | Report Agent | Produces executive summary, campaign summary, recommended actions |

### Backend

- **Framework:** FastAPI
- **LLM:** Groq (`openai/gpt-oss-20b`, `temperature=0`)
- **Orchestration:** LangGraph
- **Database:** SQLite (`data/complaints.db`)
- **Graph matching:** NetworkX (`MultiDiGraph`)
- **Language detection:** `langdetect` (offline)
- **Tracing:** LangSmith (free tier)

### Frontend

- **Framework:** React 19 + TypeScript + Vite
- **HTTP:** axios
- **UI:** Custom components — entity badges, risk badge, skeleton loaders, crisis chat panel

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/analyze` | Run full pipeline on a complaint message |
| POST | `/crisis` | Crisis companion — context-aware follow-up response |

### `/analyze` request
```json
{ "message": "I am Officer Rajesh from CBI..." }
```

### `/analyze` response shape
```json
{
  "language":    { "original_language", "was_translated", "original_message", "translated_message" },
  "investigation": { "scam_type", "summary", "reason", "immediate_actions" },
  "entities":    { "phone_numbers", "upi_ids", "emails", "urls", "bank_accounts", "telegram_ids", "amounts", "government_authorities" },
  "fraud_graph": { "id", "created_at", "scam_type", "raw_message", "entities" },
  "intelligence":{ "matched_complaints", "match_count", "campaign_detected" },
  "risk":        { "risk_score", "severity", "risk_factors" },
  "guidance":    { "helpline", "portal", "steps", "do_not", "preserve_evidence" },
  "report":      { "executive_summary", "campaign_summary", "evidence", "recommended_actions" }
}
```

---

## Agents

### `language_agent.py`
Detects input language using `langdetect`. If not English, uses the LLM to translate. Stores original language and message. All downstream agents receive English regardless of input language.

### `investigation_agent.py`
Classifies the scam type, writes a 2–3 sentence summary, explains the suspicious signals, and recommends immediate actions.

### `entity_agent.py`
Extracts structured indicators from unstructured complaint text. Includes a post-processing step that fixes UPI ID / email misclassification (e.g. `fraud@ybl` correctly lands in `upi_ids`, not `emails`) and deduplicates all entity lists.

### `intelligence_agent.py`
Queries the NetworkX graph for related complaints by shared entity values. Uses only high/medium confidence entities for matching to reduce false positives. Returns matched complaint IDs, match count, and a campaign detection flag.

### `campaign_agent.py`
Runs only when `campaign_detected` is `True`. Names the campaign, identifies signature tactics across matched complaints, and lists shared indicators. Wired via a conditional edge in the LangGraph workflow — skipped entirely for isolated incidents.

### `risk_agent.py`
Scores each complaint deterministically (0–100) based on signals: government authority impersonation (+25), UPI transfer vector (+15), phone number (+10), Telegram (+10), URL (+10), high-value amount (+10), pressure tactics like "arrest" (+15), campaign detected (+20), large campaign 5+ (+10). The LLM is only used to write the `risk_factors` explanation — the number is always consistent.

### `guidance_agent.py`
Generates scam-specific victim guidance using the actual extracted entities. Helpline (`1930`) and portal (`https://cybercrime.gov.in`) are hardcoded constants — never left to the LLM.

### `report_agent.py`
Generates the final intelligence report with executive summary, campaign context, evidence list, and recommended actions.

### `crisis_agent.py`
Powers the `/crisis` endpoint. Takes the full analysis and a user reply, returns a safe contextual response with `message`, `next_question`, and `options` for quick replies.

---

## Data Layer

Complaints are stored in `data/complaints.db` (SQLite).

**Schema:**
```sql
CREATE TABLE complaints (
    id          TEXT PRIMARY KEY,
    created_at  TEXT,
    scam_type   TEXT,
    raw_message TEXT,
    entities    TEXT   -- JSON blob
)
```

The `graph_db/graph_manager.py` module handles all DB operations and graph building:
- `save_complaint` — upserts, deduplicates by ID, marks graph dirty
- `load_complaints` — returns all complaints as dicts
- `find_related_complaints` — rebuilds NetworkX graph only when dirty (thread-safe via `threading.Lock`)
- `get_stats` — complaint counts by scam type
- `list_complaints_paged` — paginated list

---

## Frontend

Located in `frontend/src/App.tsx`. Key components:

- **Risk Badge** — colored CRITICAL / HIGH / MEDIUM / LOW badge shown at the top of results
- **Entity Badges** — colored chips per entity type (phone = blue, UPI = green, URL = red, etc.)
- **Intelligence Card** — campaign alert banner + linked complaint list
- **Guidance Card** — steps, DO NOT list, evidence checklist, hardcoded helpline and portal
- **Report Card** — executive summary, recommended actions, copy-to-clipboard button
- **Crisis Companion** — chat panel pre-loaded with analysis context, quick-reply option buttons
- **Language Banner** — shown when complaint was auto-translated
- **Loading Skeletons** — 3 placeholder cards while analysis runs
- **Inline error messages** — no `alert()` popups

---

## Project Structure

```
sentinel-ai/
  backend/
    main.py                    FastAPI app, routes, logging, input validation
    llm.py                     Groq LLM client (openai/gpt-oss-20b, temperature=0)
    agents/
      language_agent.py        Language detection and translation
      investigation_agent.py   Scam classification and summary
      entity_agent.py          Entity extraction with UPI/email fix and deduplication
      intelligence_agent.py    Campaign detection via graph matching
      risk_agent.py            Deterministic risk scoring (0-100)
      guidance_agent.py        Scam-specific victim guidance
      report_agent.py          Final intelligence report
      crisis_agent.py          Interactive crisis companion responses
    graph/
      state.py                 AgentState TypedDict (all pipeline fields)
      nodes.py                 LangGraph node functions
      workflow.py              Graph definition and compilation
    graph_db/
      graph_manager.py         SQLite CRUD + NetworkX graph with dirty-flag caching
    utils/
      json_parser.py           Resilient JSON parser with fallback extraction
    data/
      complaints.db            SQLite complaint database
      complaints.json          Legacy JSON backup (can be deleted)
    .env                       Local secrets (gitignored)
    .env.example               Template for contributors
  frontend/
    src/
      App.tsx                  Full React UI with all components
      index.css                Base styles + pulse animation
    .env.local                 VITE_API_URL (gitignored)
    package.json               Dependencies and scripts
    vite.config.ts             Vite config
  docs/
    improvements.md            Pending improvements roadmap
    progress.md                Completed / pending checklist
  README.md
```

---

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install fastapi uvicorn pydantic python-dotenv langchain-groq langgraph networkx langdetect langsmith
```

Copy `.env.example` to `.env` and fill in your keys:
```
GROQ_API_KEY=your_groq_api_key_here

LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=sentinel-ai
LANGSMITH_ENDPOINT=https://apac.api.smith.langchain.com
```

Run:
```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend reads the backend URL from `frontend/.env.local`:
```
VITE_API_URL=http://127.0.0.1:8000
```

---

## Example Input

```
I am Officer Rajesh from CBI. Your Aadhaar is linked to money laundering.
Transfer ₹50000 immediately to fraud@ybl. Call me on 9876543210.
```

The pipeline will classify this as a Digital Arrest Scam, score it CRITICAL, extract the UPI ID and phone number, match it against prior complaints, and generate India-specific victim guidance with the 1930 helpline.

---

## Troubleshooting

- **Backend not starting** — confirm `GROQ_API_KEY` is set in `backend/.env`
- **Analysis fails** — check the backend terminal for logged errors; `json_parser.py` will show the raw LLM output if parsing fails
- **CORS errors** — confirm the frontend is on `http://localhost:5173` and the backend CORS config matches
- **No related complaints** — normal when the database is empty or no entity overlap exists
- **LangSmith 403 errors** — add `LANGSMITH_ENDPOINT=https://apac.api.smith.langchain.com` to `.env` if your account is on the APAC server
- **Language detection fails on very short text** — `langdetect` defaults to English for inputs under ~20 characters
