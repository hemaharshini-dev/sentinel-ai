from langgraph.graph import StateGraph, END

from graph.state import AgentState

from graph.nodes import (
    investigation_node,
    evidence_node,
    crisis_node,
    report_node,
)

builder = StateGraph(AgentState)

builder.add_node("investigation", investigation_node)
builder.add_node("evidence", evidence_node)
builder.add_node("crisis", crisis_node)
builder.add_node("report", report_node)

builder.set_entry_point("investigation")

builder.add_edge("investigation", "evidence")
builder.add_edge("evidence", "crisis")
builder.add_edge("crisis", "report")
builder.add_edge("report", END)

graph = builder.compile()