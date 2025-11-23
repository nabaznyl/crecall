"""
Session service - business logic for sessions.
"""

from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Checkpoint, Clip, Memory
from app.db.models import Session as SessionModel
from app.schemas.session import SessionCreate, SessionUpdate
from app.services.cache import get_cache_manager


class SessionService:
    """Service for managing sessions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, session_data: SessionCreate) -> SessionModel:
        """Create a new session."""
        # Duplicate guard
        existing = await self.db.execute(
            select(SessionModel).where(SessionModel.session_id == session_data.session_id)
        )
        if existing.scalar_one_or_none() is not None:
            raise ValueError("duplicate_session")
        session = SessionModel(
            session_id=session_data.session_id,
            status=session_data.status,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def list_sessions(self, limit: int = 50) -> list[SessionModel]:
        """List all sessions with caching."""
        cache = get_cache_manager()
        cache_key = f"sessions:list:{limit}"
        if cache.enabled:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        result = await self.db.execute(
            select(SessionModel).order_by(SessionModel.updated_at.desc()).limit(limit)
        )
        sessions = result.scalars().all()

        if cache.enabled:
            cache.set(cache_key, sessions, ttl=300)  # 5 minute TTL

        return sessions

    async def get_session(self, session_id: str) -> SessionModel | None:
        """Get a specific session with caching."""
        cache = get_cache_manager()
        cache_key = f"session:{session_id}"
        if cache.enabled:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        result = await self.db.execute(
            select(SessionModel).where(SessionModel.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if cache.enabled and session is not None:
            cache.set(cache_key, session, ttl=600)  # 10 minute TTL

        return session

    async def update_session(
        self, session_id: str, session_data: SessionUpdate
    ) -> SessionModel | None:
        """Update a session."""
        session = await self.get_session(session_id)
        if not session:
            return None

        if session_data.status is not None:
            session.status = session_data.status

        await self.db.commit()
        await self.db.refresh(session)

        # Invalidate cache entries
        cache = get_cache_manager()
        if cache.enabled:
            cache.delete(f"session:{session_id}")
            cache.delete("sessions:list:50")  # common list

        return session

    async def delete_session(self, session_id: str) -> None:
        """Delete a session and all associated data and invalidate cache."""
        await self.db.execute(delete(SessionModel).where(SessionModel.session_id == session_id))
        await self.db.commit()

        cache = get_cache_manager()
        if cache.enabled:
            cache.delete(f"session:{session_id}")
            cache.delete("sessions:list:50")

    async def get_session_summary(self, session_id: str) -> dict[str, Any] | None:
        """Get session summary with statistics (cached)."""
        cache = get_cache_manager()
        cache_key = f"session:summary:{session_id}"
        if cache.enabled:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        session = await self.get_session(session_id)
        if not session:
            return None

        clips_count = await self.db.scalar(
            select(func.count(Clip.id)).where(Clip.session_id == session.id)
        )
        memories_count = await self.db.scalar(
            select(func.count(Memory.id)).where(Memory.session_id == session.id)
        )
        checkpoints_count = await self.db.scalar(
            select(func.count(Checkpoint.id)).where(Checkpoint.session_id == session.id)
        )

        summary = {
            "session_id": session.session_id,
            "status": session.status,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "clips_count": clips_count or 0,
            "memories_count": memories_count or 0,
            "checkpoints_count": checkpoints_count or 0,
        }

        if cache.enabled:
            cache.set(cache_key, summary, ttl=300)

        return summary

    async def freeze_session(self, session_id: str) -> SessionModel | None:
        """Freeze session (active → frozen). Prevents new clips except recovery."""
        session = await self.get_session(session_id)
        if not session:
            return None

        if session.status != "active":
            raise ValueError(
                f"Cannot freeze session with status '{session.status}' (must be active)"
            )

        session.status = "frozen"
        await self.db.commit()
        await self.db.refresh(session)

        self._invalidate_session_cache(session_id)
        return session

    async def archive_session(self, session_id: str) -> SessionModel | None:
        """Archive session (frozen → archived). Eligible for retention pruning."""
        session = await self.get_session(session_id)
        if not session:
            return None

        if session.status != "frozen":
            raise ValueError(
                f"Cannot archive session with status '{session.status}' (must be frozen first)"
            )

        session.status = "archived"
        await self.db.commit()
        await self.db.refresh(session)

        self._invalidate_session_cache(session_id)
        return session

    async def activate_session(self, session_id: str) -> SessionModel | None:
        """Reactivate frozen session (frozen → active)."""
        session = await self.get_session(session_id)
        if not session:
            return None

        if session.status != "frozen":
            raise ValueError(
                f"Cannot activate session with status '{session.status}' (must be frozen)"
            )

        session.status = "active"
        await self.db.commit()
        await self.db.refresh(session)

        self._invalidate_session_cache(session_id)
        return session

    def _invalidate_session_cache(self, session_id: str) -> None:
        """Invalidate all cache entries for a session."""
        cache = get_cache_manager()
        if cache.enabled:
            cache.delete(f"session:{session_id}")
            cache.delete(f"session:summary:{session_id}")
            cache.delete("sessions:list:50")  # common list cache
