import logging
from llm import llm
from utils.json_parser import parse_json

logger = logging.getLogger(__name__)

# These are hardcoded constants — never left to the LLM to generate
CYBERCRIME_HELPLINE = "1930"
CYBERCRIME_PORTAL = "https://cybercrime.gov.in"


def generate_guidance(investigation: dict, entities: dict) -> dict:
    """
    Generate scam-specific victim guidance tailored to the actual
    scam type and extracted entities from this complaint.
    """

    scam_type = investigation.get("scam_type", "Unknown Fraud")

    # Build a summary of extracted entities to pass into the prompt
    # so the LLM can reference real values (actual phone numbers, UPI IDs, etc.)
    entity_summary_parts = []

    if entities.get("phone_numbers"):
        entity_summary_parts.append(f"Phone numbers: {', '.join(entities['phone_numbers'])}")
    if entities.get("upi_ids"):
        entity_summary_parts.append(f"UPI IDs: {', '.join(entities['upi_ids'])}")
    if entities.get("emails"):
        entity_summary_parts.append(f"Emails: {', '.join(entities['emails'])}")
    if entities.get("urls"):
        entity_summary_parts.append(f"URLs: {', '.join(entities['urls'])}")
    if entities.get("bank_accounts"):
        entity_summary_parts.append(f"Bank accounts: {', '.join(entities['bank_accounts'])}")
    if entities.get("telegram_ids"):
        entity_summary_parts.append(f"Telegram IDs: {', '.join(entities['telegram_ids'])}")
    if entities.get("amounts"):
        entity_summary_parts.append(f"Amounts involved: {', '.join(entities['amounts'])}")
    if entities.get("government_authorities"):
        entity_summary_parts.append(f"Impersonated authorities: {', '.join(entities['government_authorities'])}")

    entity_summary = "\n".join(entity_summary_parts) if entity_summary_parts else "No specific entities extracted."

    prompt = f"""
You are a Cybercrime Victim Support Specialist in India.

A victim has reported the following scam:
Scam type: {scam_type}
Summary: {investigation.get("summary", "")}

Extracted scam indicators from the complaint:
{entity_summary}

Your job is to generate specific, actionable guidance for this victim.

Rules:
- Reference the actual phone numbers, UPI IDs, and other indicators above — do not use placeholders
- Make the steps specific to the scam type, not generic advice
- The "do_not" list should address the specific tactics used in THIS scam
- The "preserve_evidence" list should mention the actual extracted values above
- Keep each item to one clear sentence
- Do NOT mention the helpline number or portal URL — those are added separately

Return ONLY valid JSON.

{{
    "steps": [],
    "do_not": [],
    "preserve_evidence": []
}}
"""

    response = llm.invoke(prompt)
    parsed = parse_json(response.content)

    # Inject hardcoded constants — never trust the LLM for these
    return {
        "helpline": CYBERCRIME_HELPLINE,
        "portal": CYBERCRIME_PORTAL,
        "steps": parsed.get("steps", []),
        "do_not": parsed.get("do_not", []),
        "preserve_evidence": parsed.get("preserve_evidence", []),
    }
