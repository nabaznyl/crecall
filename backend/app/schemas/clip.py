"""
Pydantic schemas for clips.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ClipBase(BaseModel):
    """Base clip schema."""
    name: Optional[str] = None
    is_auto: bool = True
    content: Dict[str, Any] = Field(default_factory=dict)
    working_directory: Optional[str] = None
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    git_dirty: bool = False


class ClipCreate(ClipBase):
    """Schema for creating a clip."""
    session_id: str


class ClipResponse(ClipBase):
    """Schema for clip response."""
    id: int
    clip_id: str
    session_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ClipList(BaseModel):
    """Schema for clip list (minimal info)."""
    id: int
    clip_id: str
    name: Optional[str]
    is_auto: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
