"""
Database models for crecall.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Session(Base):
    """Session model - represents a work session."""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(20), default="active")  # active, paused, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clips = relationship("Clip", back_populates="session", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="session", cascade="all, delete-orphan")
    checkpoints = relationship("Checkpoint", back_populates="session", cascade="all, delete-orphan")


class Clip(Base):
    """Clip model - lightweight restore point."""
    
    __tablename__ = "clips"
    
    id = Column(Integer, primary_key=True, index=True)
    clip_id = Column(String(100), unique=True, index=True, nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    name = Column(String(200), nullable=True)  # Optional custom name
    is_auto = Column(Boolean, default=True)  # Auto-generated vs manual
    
    # Clip content (JSON)
    content = Column(JSON, nullable=False)
    
    # Metadata
    working_directory = Column(String(500))
    git_branch = Column(String(200))
    git_commit = Column(String(40))
    git_dirty = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    session = relationship("Session", back_populates="clips")


class Memory(Base):
    """Memory model - tagged memory items."""
    
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=list)  # List of tags
    category = Column(String(100), nullable=True)
    importance = Column(Integer, default=0)  # 0=normal, 1=important, 2=critical
    
    # Linking
    linked_clip_id = Column(Integer, ForeignKey("clips.id"), nullable=True)
    linked_checkpoint_id = Column(Integer, ForeignKey("checkpoints.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="memories")
    linked_clip = relationship("Clip")
    linked_checkpoint = relationship("Checkpoint")


class Checkpoint(Base):
    """Checkpoint model - full checkpoint data."""
    
    __tablename__ = "checkpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    
    note = Column(Text)
    working_directory = Column(String(500))
    docker_context = Column(String(100))
    
    # Additional metadata
    extra_data = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    session = relationship("Session", back_populates="checkpoints")
