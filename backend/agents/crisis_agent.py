from llm import llm
import json


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

    return json.loads(response.content)