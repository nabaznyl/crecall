"""'clipped' API alias for legacy 'clips' endpoints.

Provides forward-compatible naming without breaking existing clients.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.clip import ClipCreate
from app.services.clip_service import ClipService
from app.db.models import Clip

router = APIRouter()


@router.post("/", response_model=None, status_code=201)
async def create_clipped(
    clip_data: ClipCreate,
    db: AsyncSession = Depends(get_db)
):
    service = ClipService(db)
    clip = await service.create_clip(clip_data)
    return {"clip_id": clip.clip_id}


@router.get("/", response_model=None)
async def list_clipped(
    session_id: str | None = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    service = ClipService(db)
    items = await service.list_clips(session_id=session_id, limit=limit)
    return [{"clip_id": c.clip_id, "created_at": c.created_at} for c in items]
