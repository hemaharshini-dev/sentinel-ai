from llm import llm
from utils.json_parser import parse_json


def crisis_response(analysis, user_reply):

    prompt = f"""
You are Sentinel AI's Crisis Companion.

Current scam analysis:
{analysis}

The user replied:
{user_reply}

Your job is to keep the user safe.

Return ONLY valid JSON.

{{
    "message":"",
    "next_question":"",
    "options":[]
}}
"""

    response = llm.invoke(prompt)

    return parse_json(response.content)
