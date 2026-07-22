from langgraph.graph import StateGraph, END

from graph.state import AgentState

from graph.nodes import (
    investigation_node,
    entity_node,
    graph_node,
    intelligence_node,
    report_node,
)

builder = StateGraph(AgentState)

builder.add_node("investigation", investigation_node)
builder.add_node("entity", entity_node)
builder.add_node("graph", graph_node)
builder.add_node("intelligence", intelligence_node)
builder.add_node("report", report_node)

builder.set_entry_point("investigation")

builder.add_edge("investigation", "entity")
builder.add_edge("entity", "graph")
builder.add_edge("graph", "intelligence")
builder.add_edge("intelligence", "report")
builder.add_edge("report", END)

graph = builder.compile()