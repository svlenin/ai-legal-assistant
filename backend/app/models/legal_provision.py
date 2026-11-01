from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.core.database import Base


class LegalProvision(Base):
    """
    Controlled knowledge base model for verified Indian Constitutional Articles,
    Statutes (Acts), and Sections.
    """
    __tablename__ = "legal_provisions"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50), index=True, nullable=False)  # "CONSTITUTION", "ACT", "RULE"
    act_or_document_name = Column(String(255), index=True, nullable=False)  # e.g., "Constitution of India"
    identifier = Column(String(100), index=True, nullable=False)  # e.g., "Article 21", "Section 154 CrPC"
    title = Column(String(500), nullable=False)
    summary_simple = Column(Text, nullable=False)  # Plain language breakdown
    full_text = Column(Text, nullable=False)
    chapter_or_part = Column(String(255), nullable=True)  # e.g., "Part III: Fundamental Rights"
    domain_category = Column(String(100), index=True, nullable=False)  # "Fundamental Rights", "Criminal Law", etc.
    keywords = Column(JSON, default=list)  # List of relevant terms
    provenance_source_url = Column(String(500), nullable=False)  # Verified official source
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
