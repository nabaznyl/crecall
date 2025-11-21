"""
Memory service - business logic for memories.
"""

from typing import List, Optional
from sqlalchemy import select, delete, or_
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
        limit: int = 20
    ) -> List[Memory]:
        """Full-text search across memories."""
        result = await self.db.execute(
            select(Memory)
            .where(Memory.content.ilike(f"%{query}%"))
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
