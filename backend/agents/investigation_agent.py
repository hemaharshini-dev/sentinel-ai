from llm import llm
import json


def investigate(message: str):

    prompt = f"""
You are a cyber fraud investigation expert.

Analyze the following message.

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
    ]
}}

Do not return markdown.
Do not return explanation.
Only JSON.
"""

    response = llm.invoke(prompt)

    return json.loads(response.content)