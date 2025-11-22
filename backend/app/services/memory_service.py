"""
Memory service - business logic for memories.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import inspect
from sqlalchemy import select, delete, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Memory, Session as SessionModel, Clip
from app.services.websocket_manager import broadcast_event
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
            # Support both async and sync-style flush (fixture compatibility)
            flush_result = self.db.flush()
            if inspect.isawaitable(flush_result):
                await flush_result
        
        # Resolve linked_clip_id from external clip_id string to internal PK
        linked_clip_pk = None
        if memory_data.linked_clip_id:
            clip_result = await self.db.execute(
                select(Clip).where(Clip.clip_id == memory_data.linked_clip_id)
            )
            clip = clip_result.scalar_one_or_none()
            if clip:
                linked_clip_pk = clip.id
        
        memory = Memory(
            session_id=session.id,
            content=memory_data.content,
            tags=memory_data.tags,
            category=memory_data.category,
            importance=memory_data.importance,
            linked_clip_id=linked_clip_pk,
            linked_checkpoint_id=memory_data.linked_checkpoint_id,
        )
        
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)

        try:
            await broadcast_event("memory.created", {"memory_id": memory.id, "session_id": memory.session_id})
        except Exception:
            pass
        
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
        try:
            await broadcast_event("memory.updated", {"memory_id": memory.id})
        except Exception:
            pass
        
        return memory
    
    async def delete_memory(self, memory_id: int) -> None:
        """Delete a memory."""
        await self.db.execute(delete(Memory).where(Memory.id == memory_id))
        await self.db.commit()
        try:
            await broadcast_event("memory.deleted", {"memory_id": memory_id})
        except Exception:
            pass
    
    async def search_memories(
        self,
        query: str,
        limit: int = 20,
        category: Optional[str] = None,
        min_importance: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search memories with lightweight relevance ranking.

        Relevance score components:
        - Text match: counts occurrences of query terms (simple LIKE match)
        - Recency: 1 / (age_days + 1)
        - Importance boost: importance * 0.5

        Returned objects include score for downstream experimentation.
        """
        stmt = select(Memory)

        # Scope to session if provided
        if session_id:
            session_result = await self.db.execute(select(SessionModel).where(SessionModel.session_id == session_id))
            session = session_result.scalar_one_or_none()
            if session:
                stmt = stmt.where(Memory.session_id == session.id)

        # Text search (basic LIKE) – split query into terms
        terms = [t.strip() for t in query.split() if t.strip()]
        if terms:
            term_conditions = [Memory.content.ilike(f"%{t}%") for t in terms]
            stmt = stmt.where(or_(*term_conditions))

        if category:
            stmt = stmt.where(Memory.category == category)
        if min_importance is not None:
            stmt = stmt.where(Memory.importance >= min_importance)
        if date_from:
            stmt = stmt.where(Memory.created_at >= date_from)
        if date_to:
            stmt = stmt.where(Memory.created_at <= date_to)

        # Execute base query
        result = await self.db.execute(stmt.order_by(Memory.created_at.desc()).limit(limit * 4))  # fetch extra for ranking prune
        memories = result.scalars().all()

        now = datetime.utcnow()
        ranked: List[Dict[str, Any]] = []
        for m in memories:
            # Post-filter by tags (any match) since DB JSON LIKE differs across engines
            if tags and m.tags:
                if not any(tag in m.tags for tag in tags):
                    continue
            age_days = (now - m.created_at.replace(tzinfo=None)).days if m.created_at else 0
            recency_score = 1 / (age_days + 1)
            text_score = 0
            content_lower = m.content.lower()
            for t in terms:
                text_score += content_lower.count(t.lower())
            importance_score = m.importance * 0.5
            total_score = text_score + recency_score + importance_score
            ranked.append({
                "memory": m,
                "score": round(total_score, 4),
                "components": {
                    "text": text_score,
                    "recency": round(recency_score, 4),
                    "importance": importance_score
                }
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:limit]
    
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
