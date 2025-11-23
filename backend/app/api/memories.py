"""
Memories API endpoints.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.memory import MemoryCreate, MemoryResponse, MemoryUpdate
from app.services.memory_service import MemoryService

router = APIRouter()


@router.post("/", response_model=MemoryResponse, status_code=201)
async def create_memory(memory_data: MemoryCreate, db: AsyncSession = Depends(get_db)):
    """Add a new memory item."""
    service = MemoryService(db)
    memory = await service.create_memory(memory_data)
    return memory


@router.get("/", response_model=list[MemoryResponse])
async def list_memories(
    session_id: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    tags: list[str] | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List memories with optional filtering."""
    service = MemoryService(db)
    memories = await service.list_memories(
        session_id=session_id, limit=limit, search_query=search, tags=tags
    )
    return memories


@router.post("/search")
async def search_memories(
    query: str = Query("", description="Search text (may be blank for filter-only searches)"),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = None,
    min_importance: int | None = Query(None, ge=0, le=2),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    tags: list[str] | None = Query(None),
    session_id: str | None = Query(None, description="Scope search to a session"),
    db: AsyncSession = Depends(get_db),
):
    """Ranked memory search.

    Scoring = text_match_count + (1/(age_days+1)) + importance*0.5
    Returns score breakdown per memory for experimentation.
    """
    service = MemoryService(db)
    ranked = await service.search_memories(
        query=query,
        limit=limit,
        category=category,
        min_importance=min_importance,
        date_from=date_from,
        date_to=date_to,
        tags=tags,
        session_id=session_id,
    )
    return {
        "query": query,
        "count": len(ranked),
        "results": [
            {
                "memory": r["memory"],
                "score": r["score"],
                "components": r["components"],
            }
            for r in ranked
        ],
        "filters": {
            "category": category,
            "min_importance": min_importance,
            "date_from": date_from,
            "date_to": date_to,
            "tags": tags,
            "session_id": session_id,
        },
        "scoring_formula": "text + recency + importance*0.5",
    }


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get list of unique memory categories."""
    service = MemoryService(db)
    categories = await service.get_categories()
    return {"categories": categories}


@router.get("/tags/popular")
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)
):
    """Get most frequently used tags."""
    service = MemoryService(db)
    tags = await service.get_popular_tags(limit=limit)
    return {"tags": tags}


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific memory by ID."""
    service = MemoryService(db)
    memory = await service.get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: int, memory_data: MemoryUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a memory item."""
    service = MemoryService(db)
    memory = await service.update_memory(memory_id, memory_data)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(memory_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a memory."""
    service = MemoryService(db)
    await service.delete_memory(memory_id)
    return None
