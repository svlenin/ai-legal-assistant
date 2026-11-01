from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class LegalProvisionBase(BaseModel):
    source_type: str  # "CONSTITUTION", "ACT", "RULE"
    act_or_document_name: str
    identifier: str
    title: str
    summary_simple: str
    full_text: str
    chapter_or_part: Optional[str] = None
    domain_category: str
    keywords: List[str] = []
    provenance_source_url: str


class LegalProvisionResponse(LegalProvisionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ConstitutionArticleSearch(BaseModel):
    query: str
    part_filter: Optional[str] = None
    limit: int = 20
