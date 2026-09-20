"""
Pydantic output schemas for all LLM agents.
Used with llm.with_structured_output() for type-safe, validated responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class InvestigationResult(BaseModel):
    scam_type: str = Field(description="Short name for the type of scam")
    summary: str = Field(description="2-3 sentence summary of the scam")
    reason: str = Field(description="Why this message is suspicious")
    immediate_actions: List[str] = Field(description="Exactly 3 immediate actions for the victim")


class EntityResult(BaseModel):
    phone_numbers: List[str] = Field(default_factory=list)
    upi_ids: List[str] = Field(default_factory=list)
    government_authorities: List[str] = Field(default_factory=list)
    amounts: List[str] = Field(default_factory=list)
    emails: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    bank_accounts: List[str] = Field(default_factory=list)
    telegram_ids: List[str] = Field(default_factory=list)


class GuidanceResult(BaseModel):
    steps: List[str] = Field(description="Step-by-step actions for the victim")
    do_not: List[str] = Field(description="Things the victim must NOT do")
    preserve_evidence: List[str] = Field(description="Evidence to screenshot or save")


class RiskFactorsResult(BaseModel):
    risk_factors: List[str] = Field(description="2-4 plain-English risk factor statements")


class ReportResult(BaseModel):
    executive_summary: str = Field(description="High-level summary of the complaint")
    campaign_summary: str = Field(description="Summary of campaign context or isolated activity")
    evidence: List[str] = Field(default_factory=list, description="Key evidence points")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended follow-up actions")


class CrisisResult(BaseModel):
    message: str = Field(description="Supportive response message for the victim")
    next_question: str = Field(description="Follow-up question to guide the victim")
    options: List[str] = Field(default_factory=list, description="Quick reply options")


class CampaignResult(BaseModel):
    campaign_name: str = Field(description="Short descriptive name for the campaign")
    estimated_victims: int = Field(description="Estimated number of victims")
    signature_tactics: List[str] = Field(description="2-4 signature tactics used in this campaign")
    shared_entities: List[str] = Field(default_factory=list, description="Entity values shared across complaints")
    threat_level: str = Field(description="Overall threat level of the campaign")
