from langgraph.graph import StateGraph, END

from graph.state import AgentState
from graph.nodes import (
    language_node,
    investigation_node,
    entity_node,
    graph_node,
    intelligence_node,
    risk_node,
    campaign_node,
    route_after_risk,
    guidance_node,
    report_node,
)

builder = StateGraph(AgentState)

builder.add_node("language",      language_node)
builder.add_node("investigation",  investigation_node)
builder.add_node("entity",         entity_node)
builder.add_node("graph",          graph_node)
builder.add_node("intelligence",   intelligence_node)
builder.add_node("risk",           risk_node)
builder.add_node("campaign",       campaign_node)
builder.add_node("guidance",       guidance_node)
builder.add_node("report",         report_node)

builder.set_entry_point("language")

builder.add_edge("language",     "investigation")
builder.add_edge("investigation", "entity")
builder.add_edge("entity",       "graph")
builder.add_edge("graph",        "intelligence")
builder.add_edge("intelligence", "risk")

# Conditional: campaign profiling only runs when a campaign is detected
builder.add_conditional_edges("risk", route_after_risk, {
    "campaign": "campaign",
    "guidance": "guidance",
})

builder.add_edge("campaign", "guidance")
builder.add_edge("guidance", "report")
builder.add_edge("report",   END)

graph = builder.compile()
