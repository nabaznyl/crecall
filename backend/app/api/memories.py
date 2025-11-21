"""
Memories API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.memory import MemoryCreate, MemoryResponse, MemoryUpdate
from app.services.memory_service import MemoryService

router = APIRouter()


@router.post("/", response_model=MemoryResponse, status_code=201)
async def create_memory(
    memory_data: MemoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a new memory item."""
    service = MemoryService(db)
    memory = await service.create_memory(memory_data)
    return memory


@router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    session_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List memories with optional filtering."""
    service = MemoryService(db)
    memories = await service.list_memories(
        session_id=session_id,
        limit=limit,
        search_query=search,
        tags=tags
    )
    return memories


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific memory by ID."""
    service = MemoryService(db)
    memory = await service.get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: int,
    memory_data: MemoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a memory item."""
    service = MemoryService(db)
    memory = await service.update_memory(memory_id, memory_data)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a memory."""
    service = MemoryService(db)
    await service.delete_memory(memory_id)
    return None


@router.post("/search")
async def search_memories(
    query: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Full-text search across memories."""
    service = MemoryService(db)
    results = await service.search_memories(query, limit=limit)
    return {"results": results, "count": len(results)}
