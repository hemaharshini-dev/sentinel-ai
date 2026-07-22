from graph_db.graph_manager import find_related_complaints


def analyze_campaign(entities):

    matches = find_related_complaints(entities)

    return {
        "matched_complaints": matches,
        "match_count": len(matches),
        "campaign_detected": len(matches) > 1
    }