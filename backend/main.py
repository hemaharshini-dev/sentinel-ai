from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import llm

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

    prompt = f"""
You are an AI fraud analyst.

Analyze the following message.

Message:
{request.message}

Return only:
1. Scam Type
2. One-line Summary
"""

    response = llm.invoke(prompt)

    return {
        "summary": response.content
    }