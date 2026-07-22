from graph.state import AgentState

from agents.investigation_agent import investigate


def investigation_node(state: AgentState):

    print("Running Investigation Agent")

    result = investigate(state["message"])

    state["investigation"] = result

    return state


def evidence_node(state: AgentState):

    print("Running Evidence Agent")

    return state


def crisis_node(state: AgentState):

    print("Running Crisis Agent")

    return state


def report_node(state: AgentState):

    print("Running Report Agent")

    return state