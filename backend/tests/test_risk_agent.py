import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.risk_agent import _compute_score, _get_severity


def test_high_risk_case():
    investigation = {"scam_type": "Digital Arrest Scam"}
    entities = {"government_authorities": ["CBI"], "upi_ids": ["fraud@ybl"], "phone_numbers": ["9876543210"], "amounts": ["50000"], "telegram_ids": [], "urls": []}
    intelligence = {"match_count": 3, "campaign_detected": True}
    score, signals = _compute_score(investigation, entities, intelligence)
    assert score >= 61, f"Expected HIGH+, got {score}"
    assert _get_severity(score) in ("HIGH", "CRITICAL")


def test_low_risk_case():
    investigation = {"scam_type": "Unknown"}
    entities = {"government_authorities": [], "upi_ids": [], "phone_numbers": [], "amounts": ["500"], "telegram_ids": [], "urls": []}
    intelligence = {"match_count": 0, "campaign_detected": False}
    score, _ = _compute_score(investigation, entities, intelligence)
    assert _get_severity(score) in ("LOW", "MEDIUM")


def test_score_capped_at_100():
    investigation = {"scam_type": "Digital Arrest Scam"}
    entities = {"government_authorities": ["CBI", "ED"], "upi_ids": ["fraud@ybl"], "phone_numbers": ["9876543210"], "amounts": ["100000"], "telegram_ids": ["@scammer"], "urls": ["http://fake.com"]}
    intelligence = {"match_count": 10, "campaign_detected": True}
    score, _ = _compute_score(investigation, entities, intelligence)
    assert score <= 100


def test_severity_thresholds():
    assert _get_severity(0) == "LOW"
    assert _get_severity(26) == "MEDIUM"
    assert _get_severity(51) == "HIGH"
    assert _get_severity(76) == "CRITICAL"
    assert _get_severity(100) == "CRITICAL"
