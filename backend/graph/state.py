from typing import TypedDict, List, Dict


class AgentState(TypedDict):
    message: str

    investigation: Dict

    entities: Dict

    fraud_graph: Dict

    intelligence: Dict

    report: Dict