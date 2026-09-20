from graph_db.graph_manager import find_related_complaints
from agents.entity_agent import get_high_confidence_values


def analyze_campaign(entities: dict) -> dict:
    """
    Match against historical complaints using only high/medium confidence
    entity values — skips low-confidence extractions to reduce false positives.
    """
    filtered = get_high_confidence_values(entities)
    matches = find_related_complaints(filtered)

    return {
        "matched_complaints": matches,
        "match_count": len(matches),
        "campaign_detected": len(matches) > 1
    }
