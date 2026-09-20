import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from utils.json_parser import parse_json


def test_clean_json():
    result = parse_json('{"scam_type": "UPI Fraud"}')
    assert result["scam_type"] == "UPI Fraud"


def test_markdown_fences():
    result = parse_json("```json\n{\"scam_type\": \"UPI Fraud\"}\n```")
    assert result["scam_type"] == "UPI Fraud"


def test_leading_prose():
    result = parse_json('Sure! Here is the result:\n{"scam_type": "FedEx Scam"}')
    assert result["scam_type"] == "FedEx Scam"


def test_trailing_prose():
    result = parse_json('{"scam_type": "Digital Arrest"}\nLet me know if you need more.')
    assert result["scam_type"] == "Digital Arrest"


def test_bad_output_raises():
    with pytest.raises(ValueError):
        parse_json("I cannot process this request.")
