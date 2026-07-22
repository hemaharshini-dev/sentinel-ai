from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import llm
from agents.investigation_agent import investigate

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

    result = investigate(request.message)

    return result