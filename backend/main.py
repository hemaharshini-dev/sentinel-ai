import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from llm import llm
from agents.investigation_agent import investigate
from agents.crisis_agent import crisis_response
from graph.workflow import graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    message: str

    @validator("message")
    def validate_message(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("message cannot be empty")
        if len(v) > 5000:
            raise ValueError("message exceeds 5000 character limit")
        return v


@app.get("/")
def home():
    return {
        "message": "Sentinel AI Backend is Running 🚀"
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        logger.info("Received analysis request")
        state = {
            "message": request.message,
            "language": {},
            "investigation": {},
            "entities": {},
            "fraud_graph": {},
            "intelligence": {},
            "risk": {},
            "guidance": {},
            "report": {}
        }
        result = graph.invoke(state)
        logger.info("Analysis completed successfully")
        return result
    except ValueError as e:
        # Covers parse_json failures (bad LLM output)
        logger.error(f"Analysis failed — bad LLM output: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed — unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


class CrisisRequest(BaseModel):
    analysis: dict
    user_reply: str

    @validator("user_reply")
    def validate_reply(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("user_reply cannot be empty")
        if len(v) > 2000:
            raise ValueError("user_reply exceeds 2000 character limit")
        return v


@app.post("/crisis")
def crisis(request: CrisisRequest):
    try:
        logger.info("Received crisis request")
        result = crisis_response(request.analysis, request.user_reply)
        logger.info("Crisis response generated successfully")
        return result
    except ValueError as e:
        logger.error(f"Crisis response failed — bad LLM output: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Crisis response failed — unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Crisis response failed. Please try again.")
