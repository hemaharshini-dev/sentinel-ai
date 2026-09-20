import sys, os, json, tempfile, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Use a temp DB so tests never touch the real complaints.db
import graph_db.graph_manager as gm
from pathlib import Path


def setup_temp_db(tmp_path):
    gm.DB_FILE = tmp_path / "test_complaints.db"
    gm._graph_dirty = True
    gm.init_db()


def test_save_and_load(tmp_path):
    setup_temp_db(tmp_path)
    complaint = {"id": "Test-001", "created_at": "2026-01-01T00:00:00Z", "scam_type": "UPI Fraud", "raw_message": "test", "entities": {"phone_numbers": ["9876543210"], "upi_ids": []}}
    gm.save_complaint(complaint)
    loaded = gm.load_complaints()
    assert len(loaded) == 1
    assert loaded[0]["id"] == "Test-001"


def test_deduplication_on_save(tmp_path):
    setup_temp_db(tmp_path)
    complaint = {"id": "Test-002", "created_at": "", "scam_type": "x", "raw_message": "", "entities": {}}
    gm.save_complaint(complaint)
    gm.save_complaint(complaint)  # save same ID twice
    assert len(gm.load_complaints()) == 1


def test_find_related_complaints(tmp_path):
    setup_temp_db(tmp_path)
    gm.save_complaint({"id": "A", "created_at": "", "scam_type": "x", "raw_message": "", "entities": {"phone_numbers": ["9999999999"], "upi_ids": []}})
    gm.save_complaint({"id": "B", "created_at": "", "scam_type": "y", "raw_message": "", "entities": {"phone_numbers": ["9999999999"], "upi_ids": []}})
    matches = gm.find_related_complaints({"phone_numbers": ["9999999999"]})
    assert "A" in matches
    assert "B" in matches


def test_stats(tmp_path):
    setup_temp_db(tmp_path)
    gm.save_complaint({"id": "S1", "created_at": "", "scam_type": "UPI Fraud", "raw_message": "", "entities": {}})
    gm.save_complaint({"id": "S2", "created_at": "", "scam_type": "UPI Fraud", "raw_message": "", "entities": {}})
    stats = gm.get_stats()
    assert stats["total_complaints"] == 2
    assert stats["by_scam_type"][0]["type"] == "UPI Fraud"
    assert stats["by_scam_type"][0]["count"] == 2
