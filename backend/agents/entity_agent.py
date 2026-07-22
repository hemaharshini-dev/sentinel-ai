from llm import llm
from utils.json_parser import parse_json


def extract_entities(message: str):

    prompt = f"""
You are a Cybercrime Entity Extraction Agent.

Extract ONLY the entities present in the message.

Rules:
- Phone numbers go into phone_numbers.
- UPI IDs (example: name@ybl, user@ibl, abc@okaxis, xyz@oksbi, etc.) MUST go into upi_ids, NOT emails.
- Email addresses (example: abc@gmail.com, user@yahoo.com) go into emails.
- Extract government agencies like CBI, ED, RBI, Customs, Police, Income Tax into government_authorities.
- Extract all monetary amounts.
- Extract URLs.
- Extract bank account numbers if present.
- Extract Telegram usernames (example: @officerraj).

Return ONLY valid JSON.

Schema:

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

    # Uncomment only while debugging
    # print(response.content)

    return parse_json(response.content)