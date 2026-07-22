from llm import llm
from utils.json_parser import parse_json


def generate_report(state):

    prompt = f"""
You are a Cyber Crime Intelligence Officer.

Generate a concise intelligence report.

Investigation:
{state["investigation"]}

Entities:
{state["entities"]}

Campaign Intelligence:
{state["intelligence"]}

Return ONLY JSON.

{{
    "executive_summary":"",
    "campaign_summary":"",
    "evidence":[],
    "recommended_actions":[]
}}
"""

    response = llm.invoke(prompt)

    return parse_json(response.content)