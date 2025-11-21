"""
Sessions API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.services.session_service import SessionService
from app.services.branch_safety import BranchSafety
from app.middleware.security import rate_limit_middleware_instance

router = APIRouter()


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new session."""
    service = SessionService(db)
    session = await service.create_session(session_data)
    return session

@router.put("/admin/rate-limit", tags=["admin"], summary="Update global request per minute limit")
async def update_rate_limit(new_limit: int):
    if new_limit < 10 or new_limit > 5000:
        raise HTTPException(status_code=400, detail="Limit out of acceptable range (10-5000)")
    if rate_limit_middleware_instance is None:
        raise HTTPException(status_code=500, detail="Rate limiter not initialized")
    rate_limit_middleware_instance.set_limit(new_limit)
    return {"updated_limit": new_limit, "effective_limit": rate_limit_middleware_instance.limit}

@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List all sessions."""
    service = SessionService(db)
    sessions = await service.list_sessions(limit=limit)
    return sessions


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific session."""
    service = SessionService(db)
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_data: SessionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update session status."""
    service = SessionService(db)
    session = await service.update_session(session_id, session_data)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a session and all associated data."""
    service = SessionService(db)
    await service.delete_session(session_id)
    return None


@router.get("/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session summary with stats."""
    service = SessionService(db)
    summary = await service.get_session_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Session not found")
    return summary


@router.get("/{session_id}/branch-status")
async def branch_status(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Analyze branch divergence and return status with suggestions."""
    status = await BranchSafety.analyze(db, session_identifier=session_id)
    if not status.get("exists"):
        raise HTTPException(status_code=404, detail="Session not found")
    return status
