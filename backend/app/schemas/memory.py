"""
Pydantic schemas for memories.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MemoryBase(BaseModel):
    """Base memory schema."""
    content: str
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    importance: int = Field(default=0, ge=0, le=2)


class MemoryCreate(MemoryBase):
    """Schema for creating a memory."""
    session_id: str
    linked_clip_id: Optional[int] = None
    linked_checkpoint_id: Optional[int] = None


class MemoryUpdate(BaseModel):
    """Schema for updating a memory."""
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    importance: Optional[int] = Field(None, ge=0, le=2)


class MemoryResponse(MemoryBase):
    """Schema for memory response."""
    id: int
    session_id: int
    linked_clip_id: Optional[int]
    linked_checkpoint_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
