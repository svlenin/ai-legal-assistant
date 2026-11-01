from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ScenarioAnalyzeRequest(BaseModel):
    raw_query: str = Field(..., min_length=5, description="Natural language description of the scenario")
    language: str = Field(default="en", description="User interface language (en, hi, ta)")


class ExtractedFacts(BaseModel):
    actors: List[str] = Field(default_factory=list, description="Parties/persons involved")
    key_events: List[str] = Field(default_factory=list, description="Timeline of actions/events")
    location: Optional[str] = Field(None, description="Location / State / Jurisdiction")
    legal_issue: Optional[str] = Field(None, description="Core grievance or inquiry")
    action_type: Optional[str] = Field(None, description="Civil, criminal, constitutional, etc.")


class ScenarioAnalyzeResponse(BaseModel):
    scenario_id: Optional[int] = None
    extracted_facts: ExtractedFacts
    identified_domains: List[str]
    risk_level: str  # STANDARD, URGENT, HIGH_RISK
    urgency_advisory: Optional[str] = None
    clarification_questions: List[str] = []
