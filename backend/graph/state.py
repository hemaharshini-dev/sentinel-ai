from typing import TypedDict, Dict


class AgentState(TypedDict):
    message: str
    language: Dict
    investigation: Dict
    entities: Dict
    fraud_graph: Dict
    intelligence: Dict
    risk: Dict
    report: Dict
