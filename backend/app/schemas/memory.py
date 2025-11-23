"""
Pydantic schemas for memories.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class MemoryBase(BaseModel):
    """Base memory schema."""

    content: str
    tags: list[str] = Field(default_factory=list)
    category: str | None = None
    importance: int = Field(default=0, ge=0, le=2)


class MemoryCreate(MemoryBase):
    """Schema for creating a memory."""

    session_id: str  # External session identifier
    linked_clip_id: str | None = None  # External clip identifier (clip_id)
    linked_checkpoint_id: int | None = None


class MemoryUpdate(BaseModel):
    """Schema for updating a memory."""

    content: str | None = None
    tags: list[str] | None = None
    category: str | None = None
    importance: int | None = Field(None, ge=0, le=2)


class MemoryResponse(MemoryBase):
    """Schema for memory response."""

    id: int
    session_id: int
    linked_clip_id: int | None
    linked_checkpoint_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
