from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import llm
from agents.investigation_agent import investigate
from agents.crisis_agent import crisis_response
from graph.workflow import graph


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


@app.get("/")
def home():
    return {
        "message": "Sentinel AI Backend is Running 🚀"
    }




@app.post("/analyze")
def analyze(request: AnalyzeRequest):

    state = {
        "message": request.message,
        "investigation": {},
        "entities": {},
        "fraud_graph": {},
        "intelligence": {},
        "report": {}
    }

    return graph.invoke(state)


class CrisisRequest(BaseModel):
    analysis: dict
    user_reply: str


@app.post("/crisis")
def crisis(request: CrisisRequest):

    return crisis_response(
        request.analysis,
        request.user_reply
    )