"""
Clip service - business logic for clips.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.models import Clip, Session as SessionModel
from app.services.websocket_manager import broadcast_event
from app.services.retention import get_retention_manager
from app.services.integrity import Integrity
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
        
        # Compute integrity signature for content if possible
        content_payload = clip_data.content
        if isinstance(content_payload, dict):
            sig = Integrity.sign_dict(content_payload)
            if sig:
                content_payload = {**content_payload, "integrity": sig}

        clip = Clip(
            clip_id=clip_id,
            session_id=clip_data.session_id,  # This is already an integer FK
            name=clip_data.name,
            is_auto=clip_data.is_auto,
            content=content_payload,
            working_directory=clip_data.working_directory,
            git_branch=clip_data.git_branch,
            git_commit=clip_data.git_commit,
            git_dirty=clip_data.git_dirty,
        )
        
        self.db.add(clip)
        await self.db.commit()
        await self.db.refresh(clip)

        # Broadcast event (non-critical)
        try:
            await broadcast_event("clip.created", {"clip_id": clip.clip_id, "session_id": clip.session_id})
        except Exception:
            pass

        # Auto retention enforcement
        try:
            raw_fk = getattr(clip, "session_id", None)
            session_fk: Optional[int] = raw_fk if isinstance(raw_fk, int) else None
            if session_fk is not None:
                await get_retention_manager().auto_prune_if_needed(self.db, session_id=session_fk)
        except Exception:
            pass
        
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
        clips_seq = result.scalars().all()
        return list(clips_seq)
    
    async def get_clip(self, clip_id: str) -> Optional[Clip]:
        """Get a specific clip."""
        result = await self.db.execute(select(Clip).where(Clip.clip_id == clip_id))
        clip = result.scalar_one_or_none()
        if clip and isinstance(clip.content, dict):
            integrity_state = Integrity.status_dict(clip.content)
            if integrity_state == "invalid":
                # Optionally flag; here we attach marker in content for caller awareness
                clip.content["integrity_status"] = "invalid"
        return clip
    
    async def delete_clip(self, clip_id: str) -> None:
        """Delete a clip."""
        await self.db.execute(delete(Clip).where(Clip.clip_id == clip_id))
        await self.db.commit()
        try:
            await broadcast_event("clip.deleted", {"clip_id": clip_id})
        except Exception:
            pass
    
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
                raw_created = getattr(clip, "created_at", None)
                created_at_val = raw_created if isinstance(raw_created, datetime) else None
                if created_at_val is not None:
                    if created_at_val < cutoff_date:
                        if clip.id not in clips_to_delete:
                            clips_to_delete.append(clip.id)
        
        # Delete clips
        if clips_to_delete:
            await self.db.execute(
                delete(Clip).where(Clip.id.in_(clips_to_delete))
            )
            await self.db.commit()
        
        return len(clips_to_delete)
