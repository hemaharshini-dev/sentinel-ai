import logging
from llm import llm
from utils.json_parser import parse_json
from agents.entity_agent import get_flat_values

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Signal weights
# ---------------------------------------------------------------------------

SEVERITY_THRESHOLDS = [
    (76, "CRITICAL"),
    (51, "HIGH"),
    (26, "MEDIUM"),
    (0,  "LOW"),
]


def _compute_score(investigation: dict, entities: dict, intelligence: dict) -> tuple[int, list[str]]:
    """
    Deterministically calculate a risk score (0-100) from pipeline signals.
    Returns (score, list_of_triggered_signals).
    """
    score = 0
    triggered = []

    # --- Entity-based signals ---
    authorities = entities.get("government_authorities", [])
    if authorities:
        score += 25
        triggered.append(f"Government authority impersonation: {', '.join(authorities)}")

    if entities.get("upi_ids"):
        score += 15
        triggered.append(f"UPI transfer vector identified: {', '.join(entities['upi_ids'])}")

    if entities.get("phone_numbers"):
        score += 10
        triggered.append(f"Direct phone contact vector: {', '.join(entities['phone_numbers'])}")

    if entities.get("telegram_ids"):
        score += 10
        triggered.append(f"Untraced Telegram channel: {', '.join(entities['telegram_ids'])}")

    if entities.get("urls"):
        score += 10
        triggered.append(f"Suspicious URL present: {', '.join(entities['urls'])}")

    amounts = entities.get("amounts", [])
    for amt in amounts:
        # Strip non-numeric characters to compare
        digits = "".join(c for c in str(amt) if c.isdigit())
        if digits and int(digits) >= 10000:
            score += 10
            triggered.append(f"High-value transaction: {amt}")
            break

    # --- Investigation-based signals ---
    scam_type = investigation.get("scam_type", "").lower()
    high_pressure_keywords = ["arrest", "kidnap", "raid", "warrant", "case", "legal"]
    for kw in high_pressure_keywords:
        if kw in scam_type:
            score += 15
            triggered.append(f"Extreme psychological pressure tactic detected: '{scam_type}'")
            break

    # --- Campaign / intelligence signals ---
    match_count = intelligence.get("match_count", 0)
    if match_count >= 2:
        score += 20
        triggered.append(f"Organised campaign detected — {match_count} related complaints found")
    if match_count >= 5:
        score += 10
        triggered.append(f"Large-scale active campaign — {match_count} victims identified")

    # Cap at 100
    score = min(score, 100)
    return score, triggered


def _get_severity(score: int) -> str:
    for threshold, label in SEVERITY_THRESHOLDS:
        if score >= threshold:
            return label
    return "LOW"


def assess_risk(investigation: dict, entities: dict, intelligence: dict) -> dict:
    # Flatten confidence-annotated entities to plain string lists for scoring
    flat = get_flat_values(entities)
    score, triggered_signals = _compute_score(investigation, flat, intelligence)
    severity = _get_severity(score)

    logger.info(f"Risk score computed: {score} ({severity})")

    # Ask the LLM to turn the raw signals into plain-English risk factors
    prompt = f"""
You are a Cyber Crime Risk Analyst.

A fraud complaint has been scored {score}/100 with severity {severity}.

The following signals were detected:
{chr(10).join(f'- {s}' for s in triggered_signals) if triggered_signals else '- No major signals detected'}

Scam type identified: {investigation.get('scam_type', 'Unknown')}

Write 2-4 concise risk factor statements explaining why this complaint received this score.
Each statement should be one clear sentence.

Return ONLY valid JSON.

{{
    "risk_factors": []
}}
"""

    response = llm.invoke(prompt)
    parsed = parse_json(response.content)
    risk_factors = parsed.get("risk_factors", triggered_signals)

    return {
        "risk_score": score,
        "severity": severity,
        "risk_factors": risk_factors,
    }
