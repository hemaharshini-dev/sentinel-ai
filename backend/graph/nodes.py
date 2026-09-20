import logging
import uuid
from datetime import datetime, timezone

from graph.state import AgentState
from agents.investigation_agent import investigate
from agents.entity_agent import extract_entities
from agents.intelligence_agent import analyze_campaign
from agents.report_agent import generate_report
from agents.risk_agent import assess_risk
from agents.language_agent import detect_and_translate
from agents.guidance_agent import generate_guidance
from agents.campaign_agent import profile_campaign
from graph_db.graph_manager import save_complaint
from agents.entity_agent import get_flat_values

logger = logging.getLogger(__name__)


def language_node(state: AgentState):
    logger.info("Running Language Detection Agent")
    result = detect_and_translate(state["message"])
    state["language"] = result
    state["message"] = result["translated_message"]
    return state


def investigation_node(state: AgentState):
    logger.info("Running Investigation Agent")
    state["investigation"] = investigate(state["message"])
    return state


def entity_node(state: AgentState):
    logger.info("Running Entity Extraction Agent")
    state["entities"] = extract_entities(state["message"])
    return state


def graph_node(state):
    logger.info("Running Fraud Graph Builder")

    # Store flat string values in DB — confidence dicts are for pipeline use only
    flat_entities = get_flat_values(state["entities"])

    complaint = {
        "id": f"Complaint-{uuid.uuid4().hex[:8]}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scam_type": state["investigation"].get("scam_type", "unknown"),
        "raw_message": state["message"],
        "entities": flat_entities
    }

    save_complaint(complaint)
    state["fraud_graph"] = complaint
    return state


def intelligence_node(state):
    logger.info("Running Campaign Intelligence Agent")
    state["intelligence"] = analyze_campaign(state["entities"])
    return state


def risk_node(state):
    logger.info("Running Risk Scoring Agent")
    state["risk"] = assess_risk(
        state["investigation"],
        state["entities"],
        state["intelligence"],
    )
    return state


def campaign_node(state):
    logger.info("Running Campaign Profiling Agent")
    state["campaign"] = profile_campaign(state["intelligence"])
    return state


def route_after_risk(state) -> str:
    """Conditional router — run campaign profiling only when a campaign is detected."""
    if state["intelligence"].get("campaign_detected", False):
        return "campaign"
    return "guidance"


def guidance_node(state):
    logger.info("Running Victim Guidance Agent")
    state["guidance"] = generate_guidance(
        state["investigation"],
        state["entities"],
    )
    return state


def report_node(state):
    logger.info("Running Report Agent")
    state["report"] = generate_report(state)
    return state
