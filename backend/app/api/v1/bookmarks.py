from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.bookmark import Bookmark
from app.models.legal_provision import LegalProvision
from app.schemas.legal_provision import LegalProvisionResponse

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


class BookmarkCreate(BaseModel):
    user_id: int
    provision_id: int
    notes: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: int
    user_id: int
    provision_id: int
    notes: Optional[str]
    provision: Optional[LegalProvisionResponse] = None

    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def add_bookmark(payload: BookmarkCreate, db: AsyncSession = Depends(get_db)):
    bm = Bookmark(
        user_id=payload.user_id,
        provision_id=payload.provision_id,
        notes=payload.notes
    )
    db.add(bm)
    await db.commit()
    await db.refresh(bm)
    return bm


@router.get("/user/{user_id}", response_model=List[BookmarkResponse])
async def get_user_bookmarks(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bookmark).where(Bookmark.user_id == user_id))
    return result.scalars().all()
