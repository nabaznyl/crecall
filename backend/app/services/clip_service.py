"""
Clip service - business logic for clips.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.models import Clip, Session as SessionModel
from app.schemas.clip import ClipCreate


class ClipService:
    """Service for managing clips."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_clip(self, clip_data: ClipCreate) -> Clip:
        """Create a new clip."""
        # session_id in ClipCreate is now an integer FK, not a session_id string lookup
        # No need to look up session - just use the provided ID
        
        # Generate clip ID
        clip_id = f"clip-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        
        clip = Clip(
            clip_id=clip_id,
            session_id=clip_data.session_id,  # This is already an integer FK
            name=clip_data.name,
            is_auto=clip_data.is_auto,
            content=clip_data.content,
            working_directory=clip_data.working_directory,
            git_branch=clip_data.git_branch,
            git_commit=clip_data.git_commit,
            git_dirty=clip_data.git_dirty,
        )
        
        self.db.add(clip)
        await self.db.commit()
        await self.db.refresh(clip)
        
        return clip
    
    async def list_clips(
        self,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Clip]:
        """List clips."""
        query = select(Clip).order_by(Clip.created_at.desc()).limit(limit)
        
        if session_id:
            session_result = await self.db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            )
            session = session_result.scalar_one_or_none()
            if session:
                query = query.where(Clip.session_id == session.id)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_clip(self, clip_id: str) -> Optional[Clip]:
        """Get a specific clip."""
        result = await self.db.execute(
            select(Clip).where(Clip.clip_id == clip_id)
        )
        return result.scalar_one_or_none()
    
    async def delete_clip(self, clip_id: str) -> None:
        """Delete a clip."""
        await self.db.execute(
            delete(Clip).where(Clip.clip_id == clip_id)
        )
        await self.db.commit()
    
    async def prune_clips(
        self,
        keep_last: int = 100,
        older_than_days: Optional[int] = None
    ) -> int:
        """Prune old clips based on retention policy."""
        # Get all clips ordered by creation date
        result = await self.db.execute(
            select(Clip).order_by(Clip.created_at.desc())
        )
        all_clips = result.scalars().all()
        
        # Determine which clips to delete
        clips_to_delete = []
        
        # Keep last N clips
        if len(all_clips) > keep_last:
            clips_to_delete.extend([c.id for c in all_clips[keep_last:]])
        
        # Also delete clips older than specified days
        if older_than_days:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            for clip in all_clips:
                if clip.created_at < cutoff_date and clip.id not in clips_to_delete:
                    clips_to_delete.append(clip.id)
        
        # Delete clips
        if clips_to_delete:
            await self.db.execute(
                delete(Clip).where(Clip.id.in_(clips_to_delete))
            )
            await self.db.commit()
        
        return len(clips_to_delete)
