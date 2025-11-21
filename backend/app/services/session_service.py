"""
Session service - business logic for sessions.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Session as SessionModel, Clip, Memory, Checkpoint
from app.schemas.session import SessionCreate, SessionUpdate


class SessionService:
    """Service for managing sessions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(self, session_data: SessionCreate) -> SessionModel:
        """Create a new session."""
        session = SessionModel(
            session_id=session_data.session_id,
            status=session_data.status,
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def list_sessions(self, limit: int = 50) -> List[SessionModel]:
        """List all sessions."""
        result = await self.db.execute(
            select(SessionModel)
            .order_by(SessionModel.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_session(self, session_id: str) -> Optional[SessionModel]:
        """Get a specific session."""
        result = await self.db.execute(
            select(SessionModel).where(SessionModel.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def update_session(
        self,
        session_id: str,
        session_data: SessionUpdate
    ) -> Optional[SessionModel]:
        """Update a session."""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        if session_data.status is not None:
            session.status = session_data.status
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def delete_session(self, session_id: str) -> None:
        """Delete a session and all associated data."""
        await self.db.execute(
            delete(SessionModel).where(SessionModel.session_id == session_id)
        )
        await self.db.commit()
    
    async def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session summary with statistics."""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        # Count related items
        clips_count = await self.db.scalar(
            select(func.count(Clip.id)).where(Clip.session_id == session.id)
        )
        
        memories_count = await self.db.scalar(
            select(func.count(Memory.id)).where(Memory.session_id == session.id)
        )
        
        checkpoints_count = await self.db.scalar(
            select(func.count(Checkpoint.id)).where(Checkpoint.session_id == session.id)
        )
        
        return {
            "session_id": session.session_id,
            "status": session.status,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "clips_count": clips_count or 0,
            "memories_count": memories_count or 0,
            "checkpoints_count": checkpoints_count or 0,
        }
