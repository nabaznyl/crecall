"""
Pydantic schemas for sessions.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SessionBase(BaseModel):
    """Base session schema."""
    status: str = "active"


class SessionCreate(SessionBase):
    """Schema for creating a session."""
    session_id: str


class SessionUpdate(BaseModel):
    """Schema for updating a session."""
    status: Optional[str] = None


class SessionResponse(SessionBase):
    """Schema for session response."""
    id: int
    session_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
