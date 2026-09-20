import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from graph.workflow import graph
from agents.crisis_agent import crisis_response
from graph_db.graph_manager import get_stats, list_complaints_paged, get_complaint

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App + rate limiter
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Sentinel AI", version="2.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("message cannot be empty")
        if len(v) > 5000:
            raise ValueError("message exceeds 5000 character limit")
        return v


class CrisisRequest(BaseModel):
    analysis: dict
    user_reply: str

    @field_validator("user_reply")
    @classmethod
    def validate_reply(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("user_reply cannot be empty")
        if len(v) > 2000:
            raise ValueError("user_reply exceeds 2000 character limit")
        return v


# ---------------------------------------------------------------------------
# Core endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    return {"message": "Sentinel AI Backend is Running 🚀"}


@app.post("/analyze")
@limiter.limit("10/minute")
def analyze(request: Request, body: AnalyzeRequest):
    try:
        logger.info("Received analysis request")
        state = {
            "message": body.message,
            "language": {},
            "investigation": {},
            "entities": {},
            "fraud_graph": {},
            "intelligence": {},
            "risk": {},
            "campaign": {},
            "guidance": {},
            "report": {}
        }
        result = graph.invoke(state)
        logger.info("Analysis completed successfully")
        return result
    except ValueError as e:
        logger.error(f"Analysis failed — bad LLM output: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed — unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


@app.post("/crisis")
@limiter.limit("20/minute")
def crisis(request: Request, body: CrisisRequest):
    try:
        logger.info("Received crisis request")
        result = crisis_response(body.analysis, body.user_reply)
        logger.info("Crisis response generated successfully")
        return result
    except ValueError as e:
        logger.error(f"Crisis response failed — bad LLM output: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Crisis response failed — unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Crisis response failed. Please try again.")


# ---------------------------------------------------------------------------
# Data endpoints
# ---------------------------------------------------------------------------

@app.get("/stats")
def stats():
    """Total complaints and breakdown by scam type."""
    try:
        return get_stats()
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve stats.")


@app.get("/complaints")
def list_complaints(page: int = 1, limit: int = 20):
    """Paginated list of complaints (id, created_at, scam_type only)."""
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    try:
        return list_complaints_paged(page, limit)
    except Exception as e:
        logger.error(f"List complaints failed: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve complaints.")


@app.get("/complaints/{complaint_id}")
def get_single_complaint(complaint_id: str):
    """Full detail for a single complaint by ID."""
    try:
        complaint = get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(status_code=404, detail=f"Complaint '{complaint_id}' not found.")
        return complaint
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get complaint failed: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve complaint.")


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Deep health check — confirms DB is reachable and returns complaint count."""
    try:
        s = get_stats()
        return {
            "status": "ok",
            "complaints_stored": s["total_complaints"],
            "scam_types_seen": len(s["by_scam_type"]),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed.")
