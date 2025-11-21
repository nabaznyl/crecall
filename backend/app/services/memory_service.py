"""
Memory service - business logic for memories.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, delete, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Memory, Session as SessionModel
from app.schemas.memory import MemoryCreate, MemoryUpdate


class MemoryService:
    """Service for managing memories."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_memory(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory."""
        # Get or create session
        session_result = await self.db.execute(
            select(SessionModel).where(SessionModel.session_id == memory_data.session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            session = SessionModel(session_id=memory_data.session_id)
            self.db.add(session)
            await self.db.flush()
        
        memory = Memory(
            session_id=session.id,
            content=memory_data.content,
            tags=memory_data.tags,
            category=memory_data.category,
            importance=memory_data.importance,
            linked_clip_id=memory_data.linked_clip_id,
            linked_checkpoint_id=memory_data.linked_checkpoint_id,
        )
        
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        
        return memory
    
    async def list_memories(
        self,
        session_id: Optional[str] = None,
        limit: int = 20,
        search_query: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Memory]:
        """List memories with optional filtering."""
        query = select(Memory).order_by(Memory.created_at.desc()).limit(limit)
        
        if session_id:
            session_result = await self.db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            )
            session = session_result.scalar_one_or_none()
            if session:
                query = query.where(Memory.session_id == session.id)
        
        if search_query:
            query = query.where(Memory.content.ilike(f"%{search_query}%"))
        
        # Note: Tag filtering would need JSON operators (different for SQLite vs PostgreSQL)
        # Simplified for now
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_memory(self, memory_id: int) -> Optional[Memory]:
        """Get a specific memory."""
        result = await self.db.execute(
            select(Memory).where(Memory.id == memory_id)
        )
        return result.scalar_one_or_none()
    
    async def update_memory(
        self,
        memory_id: int,
        memory_data: MemoryUpdate
    ) -> Optional[Memory]:
        """Update a memory."""
        memory = await self.get_memory(memory_id)
        if not memory:
            return None
        
        if memory_data.content is not None:
            memory.content = memory_data.content
        if memory_data.tags is not None:
            memory.tags = memory_data.tags
        if memory_data.category is not None:
            memory.category = memory_data.category
        if memory_data.importance is not None:
            memory.importance = memory_data.importance
        
        await self.db.commit()
        await self.db.refresh(memory)
        
        return memory
    
    async def delete_memory(self, memory_id: int) -> None:
        """Delete a memory."""
        await self.db.execute(
            delete(Memory).where(Memory.id == memory_id)
        )
        await self.db.commit()
    
    async def search_memories(
        self,
        query: str,
        limit: int = 20,
        category: Optional[str] = None,
        min_importance: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> List[Memory]:
        """
        Advanced full-text search across memories with filtering.
        
        Args:
            query: Search text (searches in content)
            limit: Maximum results to return
            category: Filter by category
            min_importance: Minimum importance level (1-5)
            date_from: Filter memories created after this date
            date_to: Filter memories created before this date
            tags: Filter by tags (matches any tag in list)
        """
        # Build base query
        stmt = select(Memory)
        
        # Text search
        if query:
            stmt = stmt.where(Memory.content.ilike(f"%{query}%"))
        
        # Category filter
        if category:
            stmt = stmt.where(Memory.category == category)
        
        # Importance filter
        if min_importance is not None:
            stmt = stmt.where(Memory.importance >= min_importance)
        
        # Date range filter
        if date_from:
            stmt = stmt.where(Memory.created_at >= date_from)
        if date_to:
            stmt = stmt.where(Memory.created_at <= date_to)
        
        # Tags filter (SQLite JSON support is limited, so we'll do basic containment)
        # For production with PostgreSQL, use proper JSON operators
        if tags:
            tag_conditions = []
            for tag in tags:
                # This works for SQLite with JSON stored as text
                tag_conditions.append(Memory.tags.cast(str).ilike(f"%{tag}%"))
            if tag_conditions:
                stmt = stmt.where(or_(*tag_conditions))
        
        # Order by relevance (most recent first, then by importance)
        stmt = stmt.order_by(Memory.importance.desc(), Memory.created_at.desc())
        stmt = stmt.limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        result = await self.db.execute(
            select(Memory.category).distinct().where(Memory.category.isnot(None))
        )
        return [cat for cat in result.scalars().all() if cat]
    
    async def get_popular_tags(self, limit: int = 20) -> List[dict]:
        """Get most frequently used tags."""
        # This is a simplified version for SQLite
        # For production, use proper JSON aggregation
        result = await self.db.execute(
            select(Memory.tags).where(Memory.tags.isnot(None))
        )
        
        tag_counts = {}
        for tags_json in result.scalars().all():
            if tags_json and isinstance(tags_json, list):
                for tag in tags_json:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count and return top N
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"tag": tag, "count": count} for tag, count in sorted_tags]
