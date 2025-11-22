"""
Asynchronous API endpoints for improved concurrency

Converts blocking I/O operations to async for better performance.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Session as SessionModel, Clip, Memory
from app.services.cache import get_cache_manager, cached
from app.services.websocket_manager import manager, broadcast_event
from app.db.session import get_db  # Use existing async session factory

router = APIRouter(prefix="/api/async", tags=["async"])


get_async_db = get_db  # Alias for clarity


@router.get("/sessions")
@cached(ttl=60, key_prefix="async_sessions")
async def list_sessions_async(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    """
    List sessions asynchronously with caching.
    
    Benefits:
    - Non-blocking I/O
    - Response caching
    - Better concurrency
    """
    # Async query pattern
    # stmt = select(SessionModel).offset(skip).limit(limit)
    # result = await db.execute(stmt)
    # sessions = result.scalars().all()
    
    # Return cached or fresh data
    # Implement real query once models finalized
    stmt = select(SessionModel).offset(skip).limit(limit).order_by(SessionModel.updated_at.desc())
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return {"sessions": [s.session_id for s in sessions], "count": len(sessions)}


@router.get("/memories/search")
async def search_memories_async(
    q: str = Query(..., min_length=1),
    session_id: Optional[int] = None,
    limit: int = 20
):
    """
    Asynchronous semantic memory search.
    
    Features:
    - Non-blocking search
    - Parallel embedding generation
    - Cached results
    """
    cache = get_cache_manager()
    
    # Check cache first
    cache_key = f"search:{q}:{session_id}:{limit}"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return {"results": cached_result, "cached": True}
    
    # Perform search (async)
    # results = await semantic_search_async(q, session_id, limit)
    
    # Cache results
    # cache.set(cache_key, results, ttl=300)
    
    return {"message": "Async search placeholder (semantic engine integration pending)"}


@router.post("/clips/batch")
async def create_clips_batch(clips_data: List[dict]):
    """
    Create multiple clips in a single async transaction.
    
    Much faster than creating clips one-by-one.
    """
    # Async batch insert
    # async with get_async_db() as db:
    #     clips = [Clip(**data) for data in clips_data]
    #     db.add_all(clips)
    #     await db.commit()
    
    # Placeholder logic (real clip creation would use ClipService)
    await broadcast_event("clips.batch.placeholder", {"count": len(clips_data)})
    return {"message": "Batch clip creation placeholder", "requested": len(clips_data)}


# WebSocket endpoint for real-time updates
from fastapi import WebSocket, WebSocketDisconnect


# Using global manager from websocket_manager


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    """
    WebSocket endpoint for real-time session updates.
    
    Use cases:
    - Live clip creation notifications
    - Memory updates
    - Session state changes
    - Collaborative features
    
    Client example:
        const ws = new WebSocket('ws://localhost:8000/api/async/ws/123');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Update:', data);
        };
    """
    await manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Connected to real-time updates"
        })
        
        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_json()
            
            # Echo message back (can be enhanced with actual logic)
            await websocket.send_json({
                "type": "echo",
                "data": data
            })
            
            # Broadcast to other clients
            await manager.broadcast({"type": "update", "session_id": session_id, "data": data})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({
            "type": "disconnected",
            "session_id": session_id
        })
