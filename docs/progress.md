# Sentinel AI — Progress Checklist

---

## ✅ Completed

### Bug Fixes & Stability
- [x] Add `temperature=0` to LLM for deterministic JSON output
- [x] Confirm `.env` was never committed to git — API key is safe
- [x] Add `backend/.env.example` with placeholder for contributors
- [x] Fix duplicate complaint IDs corrupting the NetworkX graph
- [x] Add dirty flag + thread lock to graph manager — graph only rebuilds when new data is saved
- [x] Make `json_parser.py` resilient — fallback `{...}` extraction, clear error on total failure
- [x] Fix `crisis_agent.py` using raw `json.loads` with no protection — switched to `parse_json`
- [x] Fix UPI IDs being misclassified as emails (e.g. `fraud@ybl`)
- [x] Deduplicate entity lists — strips whitespace, removes duplicates per field
- [x] Add error handling + `HTTPException` to `/analyze` and `/crisis` endpoints
- [x] Add input validation — message capped at 5000 chars, empty messages rejected
- [x] Replace all `print` statements with structured `logging`

### Data Layer
- [x] Replace `complaints.json` with SQLite (`data/complaints.db`)
- [x] Migrate all 9 existing complaints to SQLite
- [x] Add timestamps (`created_at`), `scam_type`, and `raw_message` to every saved complaint
- [x] `get_stats()` and `list_complaints_paged()` implemented in `graph_manager.py`

### New Agents
- [x] **Risk Scoring Agent** — deterministic 0–100 score, LOW/MEDIUM/HIGH/CRITICAL severity
- [x] **Language Detection Agent** — detects language via `langdetect`, translates to English via LLM if needed (Hindi, Tamil, Telugu, Marathi, etc.)
- [x] **Victim Guidance Agent** — scam-specific steps, DO NOT list, evidence checklist, hardcoded 1930 helpline and cybercrime.gov.in portal

### Pipeline
- [x] Language node added as first step in LangGraph workflow
- [x] Risk node added between intelligence and report
- [x] Guidance node added between risk and report
- [x] Full pipeline: Language → Investigation → Entity → Graph → Intelligence → Risk → Guidance → Report
- [x] `AgentState` updated with `language`, `risk`, `guidance` fields

### Frontend
- [x] Replace raw `JSON.stringify` dumps with structured cards
- [x] Entity badges — colored chips per entity type
- [x] Risk badge — CRITICAL/HIGH/MEDIUM/LOW with color coding
- [x] Guidance card — steps, DO NOT list, evidence checklist, helpline + portal link
- [x] Intelligence card — campaign alert banner, linked complaint list
- [x] Report card — executive summary, recommended actions, copy-to-clipboard button
- [x] Crisis Companion chat panel — pre-loaded with analysis context, quick-reply buttons, auto-scroll
- [x] Language banner — shown when complaint was auto-translated
- [x] Loading skeletons — 3 placeholder cards while analysis runs
- [x] Inline error messages — replaced `alert()` popups
- [x] API base URL from `VITE_API_URL` env var — no more hardcoded `127.0.0.1:8000`
- [x] `frontend/.env.local` created

### Observability
- [x] LangSmith tracing configured (free tier)
- [x] `LANGSMITH_ENDPOINT` set for APAC region to fix 403 errors
- [x] `backend/.env.example` updated with all LangSmith vars

---

## ⏳ Pending

### Quick Wins
- [ ] Normalize entity values before graph storage (phone, amount, URL formats)
- [ ] Add LangChain `SQLiteCache` for LLM response caching — saves quota on repeated prompts
- [ ] Add rate limiting with `slowapi` — prevent quota exhaustion

### New Agents
- [ ] Campaign Profiling Agent — names campaigns, identifies signature tactics (runs only when campaign detected)
- [ ] Confidence scoring for entity extraction — weight high/low confidence entities differently in graph matching

### New API Endpoints
- [ ] Wire up `/stats` endpoint — `get_stats()` already implemented in `graph_manager.py`
- [ ] Wire up `/complaints` paginated endpoint — `list_complaints_paged()` already implemented
- [ ] Add `/health` deep health endpoint

### Frontend
- [ ] Analysis history in `localStorage` — collapsible sidebar of last 10 analyses

### Security
- [ ] Prompt injection hardening — wrap user input in `<USER_COMPLAINT>` delimiters across all agents
- [ ] Pydantic structured outputs — replace `parse_json` with `llm.with_structured_output()`

### Testing
- [ ] `pytest` unit test suite — entity agent, JSON parser, risk scoring, graph manager

---

## Stats

| Category | Done | Pending |
|---|---|---|
| Bug fixes & stability | 12 | 0 |
| Data layer | 4 | 0 |
| New agents | 3 | 2 |
| Pipeline | 5 | 0 |
| Frontend | 16 | 1 |
| Observability | 3 | 0 |
| API endpoints | 0 | 3 |
| Security | 0 | 2 |
| Testing | 0 | 1 |
| **Total** | **43** | **9** |
