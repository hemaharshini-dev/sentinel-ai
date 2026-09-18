from llm import llm
from utils.json_parser import parse_json

# Known UPI payment handle suffixes — anything @<suffix> is a UPI ID, not an email
UPI_SUFFIXES = {
    "ybl", "ibl", "oksbi", "okaxis", "okicici", "okhdfcbank",
    "paytm", "upi", "icici", "sbi", "axl", "okhdfc", "apl",
    "fbl", "pnb", "cnrb", "barodampay", "mahb", "unionbank"
}


def _fix_upi_email_split(entities: dict) -> dict:
    """
    Move any entry in emails that looks like a UPI ID (e.g. fraud@ybl)
    into upi_ids. The LLM sometimes misclassifies these despite prompt rules.
    """
    upi_ids = set(entities.get("upi_ids", []))
    clean_emails = []

    for addr in entities.get("emails", []):
        _, _, domain = addr.partition("@")
        base_domain = domain.lower().split(".")[0]
        if base_domain in UPI_SUFFIXES:
            upi_ids.add(addr)
        else:
            clean_emails.append(addr)

    entities["upi_ids"] = list(upi_ids)
    entities["emails"] = clean_emails
    return entities


def _deduplicate_entities(entities: dict) -> dict:
    """
    Remove duplicate values within each entity list while preserving order.
    Also strips whitespace from each value.
    """
    for key, val in entities.items():
        if isinstance(val, list):
            entities[key] = list(dict.fromkeys(v.strip() for v in val if v))
    return entities


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

    entities = parse_json(response.content)

    # Post-process: fix UPI/email misclassification, then deduplicate
    entities = _fix_upi_email_split(entities)
    entities = _deduplicate_entities(entities)

    return entities
