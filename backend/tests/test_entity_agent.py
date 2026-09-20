import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.entity_agent import _fix_upi_email_split, _deduplicate_entities, _score_value, get_high_confidence_values


def test_upi_moved_from_emails():
    e = {"upi_ids": [], "emails": ["fraud@ybl", "real@gmail.com", "scammer@okaxis"]}
    result = _fix_upi_email_split(e)
    assert "fraud@ybl" in result["upi_ids"]
    assert "scammer@okaxis" in result["upi_ids"]
    assert "real@gmail.com" in result["emails"]
    assert "fraud@ybl" not in result["emails"]


def test_deduplication():
    e = {"phone_numbers": ["9876543210", "9876543210", " 9876543210"], "upi_ids": []}
    result = _deduplicate_entities(e)
    assert result["phone_numbers"] == ["9876543210"]


def test_phone_confidence():
    assert _score_value("phone_numbers", "9876543210") == "high"
    assert _score_value("phone_numbers", "98765") == "low"
    assert _score_value("phone_numbers", "9876543") == "medium"


def test_upi_confidence():
    assert _score_value("upi_ids", "fraud@ybl") == "high"
    assert _score_value("upi_ids", "user@unknown") == "medium"
    assert _score_value("upi_ids", "notaupi") == "low"


def test_get_high_confidence_values_filters_low():
    entities = {
        "phone_numbers": [
            {"value": "9876543210", "confidence": "high"},
            {"value": "12345", "confidence": "low"},
        ],
        "upi_ids": [{"value": "fraud@ybl", "confidence": "high"}],
    }
    result = get_high_confidence_values(entities)
    assert "9876543210" in result["phone_numbers"]
    assert "12345" not in result["phone_numbers"]
    assert "fraud@ybl" in result["upi_ids"]
