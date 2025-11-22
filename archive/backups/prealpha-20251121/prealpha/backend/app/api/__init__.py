"""API package.

Adds context assembly endpoint stub for prompt-oriented integrations.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.clip_service import ClipService
from app.services.memory_service import MemoryService

context_router = APIRouter()

@context_router.get("/assemble")
async def assemble_context(
	limit_clips: int = 3,
	limit_memories: int = 5,
	db: AsyncSession = Depends(get_db)
):
	"""Return lightweight prompt-ready context bundle.

	This is a minimal stub; future implementation will add semantic selection,
	sanitization, and scoring fusion. For now returns recent clips + high-importance memories.
	"""
	clip_service = ClipService(db)
	memory_service = MemoryService(db)
	clips = await clip_service.list_clips(limit=limit_clips)
	memories = await memory_service.list_memories(limit=limit_memories)
	high_importance = [m for m in memories if getattr(m, 'importance', 0) >= 2]
	return {
		"clips": clips,
		"memories": high_importance,
		"meta": {
			"version": "0.1.0d-3",
			"selection": "recent+importance>=2",
		}
	}
