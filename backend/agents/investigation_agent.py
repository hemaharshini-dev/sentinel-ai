from llm import llm
from utils.json_parser import parse_json


def investigate(message: str):

    prompt = f"""
You are Sentinel AI's Investigation Agent.

Your job is to analyze suspicious cybercrime complaints.

Analyze the following message.

Message:
{message}

Tasks:
1. Identify the scam type.
2. Summarize the scam in 2-3 sentences.
3. Explain why it is suspicious.
4. Recommend exactly 3 immediate actions for the victim.

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
    ]
}}

Rules:
- Do NOT ask questions.
- Do NOT generate follow-up conversation.
- Do NOT return markdown.
- Do NOT return explanations outside JSON.
- Return ONLY valid JSON.
"""

    response = llm.invoke(prompt)

    return parse_json(response.content)