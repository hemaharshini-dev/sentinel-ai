import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.normalizers import normalize_entities


def test_phone_normalization():
    e = normalize_entities({"phone_numbers": ["+91 9876543210", "9876543210", "98765 43210"], "upi_ids": [], "amounts": [], "urls": [], "emails": []})
    assert e["phone_numbers"] == ["9876543210"]


def test_amount_normalization():
    e = normalize_entities({"phone_numbers": [], "upi_ids": [], "amounts": ["₹50,000", "50000", "₹50000"], "urls": [], "emails": []})
    assert e["amounts"] == ["50000"]


def test_url_normalization():
    e = normalize_entities({"phone_numbers": [], "upi_ids": [], "amounts": [], "urls": ["HTTP://Scam.COM/", "http://scam.com"], "emails": []})
    assert e["urls"] == ["http://scam.com"]


def test_upi_lowercased():
    e = normalize_entities({"phone_numbers": [], "upi_ids": ["Fraud@YBL", "fraud@ybl"], "amounts": [], "urls": [], "emails": []})
    assert e["upi_ids"] == ["fraud@ybl"]
