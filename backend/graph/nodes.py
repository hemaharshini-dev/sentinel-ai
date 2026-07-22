from graph.state import AgentState

from agents.investigation_agent import investigate

from agents.entity_agent import extract_entities
from agents.intelligence_agent import analyze_campaign
from graph_db.graph_manager import save_complaint
import uuid

from agents.report_agent import generate_report

def investigation_node(state: AgentState):

    print("Running Investigation Agent")

    state["investigation"] = investigate(state["message"])

    return state


def entity_node(state: AgentState):

    print("Running Entity Extraction Agent")

    entities = extract_entities(state["message"])

    state["entities"] = entities

    return state

    

def graph_node(state):

    print("Running Fraud Graph Builder")

    complaint = {
        "id": f"Complaint-{uuid.uuid4().hex[:8]}",
        "entities": state["entities"]
    }

    save_complaint(complaint)

    state["fraud_graph"] = complaint

    return state


def intelligence_node(state):

    print("Running Campaign Intelligence Agent")

    state["intelligence"] = analyze_campaign(
        state["entities"]
    )

    return state


def report_node(state):

    print("Running Report Agent")

    state["report"] = generate_report(state)

    return state