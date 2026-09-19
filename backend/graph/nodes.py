import logging
import uuid
from datetime import datetime, timezone

from graph.state import AgentState
from agents.investigation_agent import investigate
from agents.entity_agent import extract_entities
from agents.intelligence_agent import analyze_campaign
from agents.report_agent import generate_report
from agents.risk_agent import assess_risk
from graph_db.graph_manager import save_complaint

logger = logging.getLogger(__name__)


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

    complaint = {
        "id": f"Complaint-{uuid.uuid4().hex[:8]}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scam_type": state["investigation"].get("scam_type", "unknown"),
        "raw_message": state["message"],
        "entities": state["entities"]
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


def report_node(state):
    logger.info("Running Report Agent")
    state["report"] = generate_report(state)
    return state
