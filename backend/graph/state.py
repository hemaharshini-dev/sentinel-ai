from typing import TypedDict


class AgentState(TypedDict):
    message: str

    investigation: dict

    evidence: dict

    crisis: dict

    report: dict