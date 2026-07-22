from llm import llm
import json
from utils.json_parser import parse_json


def extract_entities(message: str):

    prompt = f"""
Extract all cybercrime entities.

Return ONLY JSON.

{{
    "phone_numbers": [],
    "upi_ids": [],
    "government_authorities": [],
    "amounts": [],
    "emails": [],
    "urls": [],
    "bank_accounts": [],
    "telegram_ids": []
}}

Message:
{message}
"""

    response = llm.invoke(prompt)

    print(response.content)

    return parse_json(response.content)