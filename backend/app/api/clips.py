"""
Clips API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.session import get_db
from app.schemas.clip import ClipCreate, ClipResponse, ClipList
from app.services.clip_service import ClipService

router = APIRouter()


@router.post("/", response_model=ClipResponse, status_code=201)
async def create_clip(
    clip_data: ClipCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new clip (manual or auto)."""
    service = ClipService(db)
    clip = await service.create_clip(clip_data)
    return clip


@router.get("/", response_model=List[ClipList])
@router.get("/", response_model=List[ClipList])
async def list_clips(
    session_id: Optional[str] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    service = ClipService(db)
    clips = await service.list_clips(session_id=session_id, limit=limit)
    return clips


@router.get("/{clip_id}", response_model=ClipResponse)
async def get_clip(
    clip_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific clip by ID."""
    service = ClipService(db)
    clip = await service.get_clip(clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return clip


@router.delete("/{clip_id}", status_code=204)
async def delete_clip(
    clip_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a clip."""
    service = ClipService(db)
    await service.delete_clip(clip_id)
    return None


@router.post("/prune")
async def prune_clips(
    keep_last: int = 100,
    older_than_days: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Prune old clips based on retention policy."""
    service = ClipService(db)
    deleted_count = await service.prune_clips(
        keep_last=keep_last,
        older_than_days=older_than_days
    )
    return {"deleted": deleted_count}
