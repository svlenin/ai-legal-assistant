from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.legal_provision import LegalProvisionResponse
from app.schemas.scenario import ExtractedFacts


class RecommendedProvision(BaseModel):
    provision: LegalProvisionResponse
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Retrieval relevance score (not a claim of legal certainty)")
    confidence_level: str = Field(..., description="High, Moderate, Low retrieval match")
    why_recommended: str = Field(..., description="Explainable rationale connecting extracted scenario facts to this legal provision")
    matching_facts: List[str] = Field(default_factory=list, description="Specific scenario elements that matched")
    provenance_reference: str = Field(..., description="Verified source reference")


class RecommendationResponse(BaseModel):
    scenario_id: Optional[int] = None
    extracted_facts: ExtractedFacts
    disclaimer: str
    risk_level: str
    recommendations: List[RecommendedProvision]
    plain_language_explanation: str
    follow_up_questions: List[str] = []


class WhatIfRequest(BaseModel):
    original_scenario_id: Optional[int] = None
    original_facts: ExtractedFacts
    modified_facts: ExtractedFacts


class WhatIfComparisonResponse(BaseModel):
    original_provisions: List[RecommendedProvision]
    updated_provisions: List[RecommendedProvision]
    diff_summary: str
    changes_detected: List[str]
