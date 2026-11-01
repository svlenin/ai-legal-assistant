from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.legal_provision import LegalProvision
from app.schemas.legal_provision import LegalProvisionResponse

router = APIRouter(prefix="/constitution", tags=["Constitution & Articles"])


@router.get("/articles", response_model=List[LegalProvisionResponse])
async def search_constitution_articles(
    query: Optional[str] = Query(None, description="Search query or article number"),
    part: Optional[str] = Query(None, description="Part of Constitution"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Search and explore Indian Constitutional Articles and statutory provisions.
    """
    stmt = select(LegalProvision).where(LegalProvision.source_type == "CONSTITUTION")
    if part:
        stmt = stmt.where(LegalProvision.chapter_or_part.ilike(f"%{part}%"))
    if query:
        stmt = stmt.where(
            LegalProvision.title.ilike(f"%{query}%") |
            LegalProvision.identifier.ilike(f"%{query}%") |
            LegalProvision.summary_simple.ilike(f"%{query}%")
        )
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    provisions = result.scalars().all()
    return provisions
