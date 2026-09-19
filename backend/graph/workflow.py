from langgraph.graph import StateGraph, END

from graph.state import AgentState

from graph.nodes import (
    language_node,
    investigation_node,
    entity_node,
    graph_node,
    intelligence_node,
    risk_node,
    report_node,
)

builder = StateGraph(AgentState)

builder.add_node("language", language_node)
builder.add_node("investigation", investigation_node)
builder.add_node("entity", entity_node)
builder.add_node("graph", graph_node)
builder.add_node("intelligence", intelligence_node)
builder.add_node("risk", risk_node)
builder.add_node("report", report_node)

builder.set_entry_point("language")

builder.add_edge("language", "investigation")
builder.add_edge("investigation", "entity")
builder.add_edge("entity", "graph")
builder.add_edge("graph", "intelligence")
builder.add_edge("intelligence", "risk")
builder.add_edge("risk", "report")
builder.add_edge("report", END)

graph = builder.compile()
