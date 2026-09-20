# Sentinel AI — Progress Checklist

---

## ✅ Completed

### Bug Fixes & Stability
- [x] Add `temperature=0` to LLM for deterministic JSON output
- [x] Confirm `.env` was never committed to git — API key is safe
- [x] Add `backend/.env.example` with placeholder for contributors (includes LangSmith vars)
- [x] Fix duplicate complaint IDs corrupting the NetworkX graph
- [x] Add dirty flag + thread lock to graph manager — graph only rebuilds when new data is saved
- [x] Make `json_parser.py` resilient — fallback `{...}` extraction, clear error on total failure
- [x] Fix `crisis_agent.py` using raw `json.loads` — switched to `parse_json`
- [x] Fix UPI IDs being misclassified as emails (e.g. `fraud@ybl`)
- [x] Deduplicate entity lists — strips whitespace, removes duplicates per field
- [x] Add error handling + `HTTPException` to `/analyze` and `/crisis` endpoints
- [x] Add input validation — message capped at 5000 chars, empty messages rejected
- [x] Replace all `print` statements with structured `logging`
- [x] Fix entity structure mismatch — `normalizers.py` now runs inside `entity_agent.py` before confidence annotation; `risk_agent` and `guidance_agent` use `get_flat_values()` to extract plain strings from confidence dicts
- [x] Fix `@validator` → `@field_validator` for Pydantic v2 compatibility in `main.py`
- [x] Fix `campaign_agent.py` unused `entities` parameter removed

### Data Layer
- [x] Replace `complaints.json` with SQLite (`data/complaints.db`)
- [x] Migrate all 9 existing complaints to SQLite
- [x] Add timestamps (`created_at`), `scam_type`, and `raw_message` to every saved complaint
- [x] `get_stats()`, `list_complaints_paged()`, `get_complaint()` implemented in `graph_manager.py`

### New Agents
- [x] **Risk Scoring Agent** — deterministic 0–100 score, LOW/MEDIUM/HIGH/CRITICAL severity
- [x] **Language Detection Agent** — detects language via `langdetect`, translates to English via LLM if needed
- [x] **Victim Guidance Agent** — scam-specific steps, DO NOT list, evidence checklist, hardcoded 1930 helpline and cybercrime.gov.in portal
- [x] **Campaign Profiling Agent** — names campaigns, identifies signature tactics (conditional — runs only when campaign detected)
- [x] **Confidence Scoring** — entity extraction assigns high/medium/low confidence; intelligence agent uses only high/medium values for graph matching

### Pipeline
- [x] Language node added as first step in LangGraph workflow
- [x] Risk node added between intelligence and report
- [x] Guidance node added between risk and report
- [x] Campaign node added with conditional edge — skipped when no campaign detected
- [x] Full pipeline: Language → Investigation → Entity → Graph → Intelligence → Risk → (Campaign?) → Guidance → Report
- [x] `AgentState` updated with `language`, `risk`, `campaign`, `guidance` fields

### API Endpoints
- [x] `/stats` — total complaints and breakdown by scam type
- [x] `/complaints` — paginated list (id, created_at, scam_type)
- [x] `/complaints/{id}` — full detail for a single complaint
- [x] `/health` — DB reachable, complaint count, scam types seen

### Security
- [x] Prompt injection hardening — user input wrapped in `<USER_COMPLAINT>` / `<USER_REPLY>` / `<ANALYSIS_DATA>` delimiters across all 5 agents
- [x] Rate limiting — `/analyze` capped at 10/min, `/crisis` at 20/min via `slowapi`
- [x] Input length validation on both endpoints

### Frontend
- [x] Replace raw `JSON.stringify` dumps with structured cards
- [x] Entity badges — colored chips per entity type with confidence opacity
- [x] Risk badge — CRITICAL/HIGH/MEDIUM/LOW with color coding
- [x] Guidance card — steps, DO NOT list, evidence checklist, helpline + portal link
- [x] Intelligence card — campaign alert banner, linked complaint list
- [x] Campaign Profile card — campaign name, threat level, signature tactics, shared indicators
- [x] Report card — executive summary, recommended actions, copy-to-clipboard button
- [x] Crisis Companion chat panel — pre-loaded with analysis context, quick-reply buttons, auto-scroll
- [x] Language banner — shown when complaint was auto-translated
- [x] Loading skeletons — 3 placeholder cards while analysis runs
- [x] Inline error messages — replaced `alert()` popups
- [x] API base URL from `VITE_API_URL` env var
- [x] `frontend/.env.local` created
- [x] Analysis history in `localStorage` — collapsible "Recent Analyses" sidebar, last 10 analyses

### Observability
- [x] LangSmith tracing configured (free tier)
- [x] `LANGSMITH_ENDPOINT` added to `.env.example` for APAC region
- [x] Structured logging across all nodes and agents

### Testing
- [x] `pytest` unit test suite — 22 tests across 4 test files
  - `test_entity_agent.py` — UPI/email split, deduplication, confidence scoring, high-confidence filtering
  - `test_json_parser.py` — clean JSON, fenced JSON, leading/trailing prose, broken output
  - `test_normalizers.py` — phone, amount, URL, UPI normalization and deduplication
  - `test_risk_agent.py` — signal scoring, severity thresholds, score cap

### Performance
- [x] LLM in-memory cache — identical prompts skip the API call entirely
- [x] Persistent SQLite LLM cache (`utils/cache.py`) — cache survives server restarts, built on `langchain_core.BaseCache` with no deprecated dependencies

### Code Quality
- [x] Pydantic structured outputs — all 6 agents use `llm.with_structured_output()` with typed schemas in `agents/schemas.py`; `parse_json` no longer used in any agent

---

## ⏳ Pending

None — all planned improvements are complete.

---

## Stats

| Category          | Done | Pending |
|---|---|---|
| Bug fixes & stability | 15 | 0 |
| Data layer        | 4   | 0 |
| New agents        | 5   | 0 |
| Pipeline          | 6   | 0 |
| API endpoints     | 4   | 0 |
| Security          | 3   | 0 |
| Frontend          | 14  | 0 |
| Observability     | 3   | 0 |
| Testing           | 1   | 0 |
| Performance       | 2   | 0 |
| Code quality      | 1   | 0 |
| Low priority      | 0   | 0 |
| **Total**         | **58** | **0** |
