from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from app.core.database import Base


class UserScenario(Base):
    __tablename__ = "user_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    raw_query = Column(Text, nullable=False)
    extracted_facts = Column(JSON, default=dict)
    identified_domains = Column(JSON, default=list)
    risk_level = Column(String(50), default="STANDARD")  # STANDARD, URGENT, HIGH_RISK
    recommendations_summary = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
