"""
Pydantic schemas for clips.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ClipBase(BaseModel):
    """Base clip schema."""

    name: str | None = None
    is_auto: bool = True
    content: dict[str, Any] = Field(default_factory=dict)
    working_directory: str | None = None
    git_branch: str | None = None
    git_commit: str | None = None
    git_dirty: bool = False


class ClipCreate(ClipBase):
    """Schema for creating a clip."""

    session_id: str  # External session identifier (not internal PK)
    profile: str | None = "standard"  # For clip engine: minimal, standard, complete


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
    name: str | None
    is_auto: bool
    created_at: datetime

    model_config = {"from_attributes": True}
