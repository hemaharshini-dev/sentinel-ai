from llm import llm
import json
from utils.json_parser import parse_json

def investigate(message: str):

    prompt = f"""
You are Sentinel AI's Investigation Agent.

Analyze the following suspicious message.

Message:
{message}

Return ONLY valid JSON.

Schema:

{{
    "scam_type": "",
    "summary": "",
    "reason": "",
    "immediate_actions": [
        "",
        "",
        ""
    ],
    "next_question": "",
    "options": [
        "",
        ""
    ]
}}

Rules:

- Identify the scam type.
- Explain why it is a scam.
- Give 3 immediate actions.
- Ask ONLY ONE important next question that helps protect the victim.
- If the question is Yes/No, return:
    "options": ["Yes", "No"]
- If it requires typing, return:
    "options": []

Return ONLY JSON.
Do NOT wrap it in markdown.
"""

    response = llm.invoke(prompt)

    return parse_json(response.content)