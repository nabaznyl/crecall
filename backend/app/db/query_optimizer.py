"""
Database query optimizations and best practices

This module provides optimized query patterns and utilities
for improving database performance.
"""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload, selectinload
from app.db.models import Session as SessionModel, Clip, Memory


class QueryOptimizer:
    """Optimized database query patterns"""

    @staticmethod
    def get_session_with_related(db: Session, session_id: int) -> Optional[SessionModel]:
        """
        Get session with all related data in a single query using eager loading.
        
        More efficient than:
            session = db.query(SessionModel).get(session_id)
            clips = session.clips  # N+1 query problem
        
        Args:
            db: Database session
            session_id: Session ID to fetch
            
        Returns:
            Session with eager-loaded clips and memories
        """
        stmt = (
            select(SessionModel)
            .options(
                selectinload(SessionModel.clips),
                selectinload(SessionModel.memories),
            )
            .where(SessionModel.id == session_id)
        )
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def get_recent_clips_optimized(
        db: Session, session_id: int, limit: int = 10
    ) -> List[Clip]:
        """
        Get recent clips with optimized query.
        
        Uses explicit ordering and limit at database level.
        
        Args:
            db: Database session
            session_id: Session ID
            limit: Maximum number of clips
            
        Returns:
            List of recent clips
        """
        stmt = (
            select(Clip)
            .where(Clip.session_id == session_id)
            .order_by(Clip.created_at.desc())
            .limit(limit)
        )
        result = db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def get_high_importance_memories(
        db: Session, session_id: int, min_importance: int = 2
    ) -> List[Memory]:
        """
        Get high-importance memories with efficient filtering.
        
        Args:
            db: Database session
            session_id: Session ID
            min_importance: Minimum importance level
            
        Returns:
            List of high-importance memories
        """
        stmt = (
            select(Memory)
            .where(
                Memory.session_id == session_id,
                Memory.importance >= min_importance,
            )
            .order_by(Memory.importance.desc(), Memory.created_at.desc())
        )
        result = db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def count_clips_by_session(db: Session) -> dict:
        """
        Get clip counts per session with single aggregation query.
        
        More efficient than looping through sessions.
        
        Returns:
            Dictionary mapping session_id to clip count
        """
        stmt = (
            select(Clip.session_id, func.count(Clip.clip_id))
            .group_by(Clip.session_id)
        )
        result = db.execute(stmt)
        rows = result.all()
        return {row[0]: row[1] for row in rows}

    @staticmethod
    def search_memories_optimized(
        db: Session, query: str, limit: int = 20
    ) -> List[Memory]:
        """
        Optimized memory search using database-level text search.
        
        For SQLite: Uses LIKE (consider FTS5 for production)
        For PostgreSQL: Can use full-text search
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        # SQLite LIKE search (basic)
        # For production, consider:
        # - SQLite: FTS5 virtual table
        # - PostgreSQL: to_tsvector/to_tsquery
        stmt = (
            select(Memory)
            .where(Memory.content.like(f"%{query}%"))
            .order_by(Memory.importance.desc())
            .limit(limit)
        )
        result = db.execute(stmt)
        return list(result.scalars().all())


class BatchOperations:
    """Batch database operations for efficiency"""

    @staticmethod
    def bulk_create_clips(db: Session, clips_data: List[dict]) -> List[Clip]:
        """
        Bulk create clips in a single transaction.
        
        More efficient than creating one by one.
        
        Args:
            db: Database session
            clips_data: List of clip data dictionaries
            
        Returns:
            List of created Clip objects
        """
        clips = [Clip(**data) for data in clips_data]
        db.bulk_save_objects(clips, return_defaults=True)
        db.commit()
        return clips

    @staticmethod
    def bulk_update_importance(
        db: Session, memory_ids: List[int], new_importance: int
    ):
        """
        Bulk update memory importance levels.
        
        Args:
            db: Database session
            memory_ids: List of memory IDs to update
            new_importance: New importance level
        """
        db.query(Memory).filter(Memory.id.in_(memory_ids)).update(
            {Memory.importance: new_importance}, synchronize_session=False
        )
        db.commit()


# Database indexes to add (for migration)
RECOMMENDED_INDEXES = """
-- Add these indexes in an Alembic migration for better performance

-- Sessions
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);

-- Clips
CREATE INDEX IF NOT EXISTS idx_clips_session_id ON clips(session_id);
CREATE INDEX IF NOT EXISTS idx_clips_created_at ON clips(created_at);
CREATE INDEX IF NOT EXISTS idx_clips_is_auto ON clips(is_auto);
CREATE INDEX IF NOT EXISTS idx_clips_session_created ON clips(session_id, created_at);

-- Memories
CREATE INDEX IF NOT EXISTS idx_memories_session_id ON memories(session_id);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_memories_importance_created ON memories(importance, created_at);

-- For full-text search (SQLite FTS5)
-- CREATE VIRTUAL TABLE memories_fts USING fts5(content, content='memories', content_rowid='id');

-- Triggers to keep FTS index in sync
-- CREATE TRIGGER memories_ai AFTER INSERT ON memories BEGIN
--   INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
-- END;
"""
