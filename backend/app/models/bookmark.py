from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from app.core.database import Base


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provision_id = Column(Integer, ForeignKey("legal_provisions.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
