"""Retention pruning scheduler for archived sessions and stale memories.

Rules:
- Prune archived sessions older than session_retention_days.
- Prune low-importance memories (importance <= importance_threshold) older than memory_retention_days,
  excluding those belonging to sessions slated for deletion (cascade handles them).
- Dry-run mode reports counts without deleting.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.models import Session, Memory

class RetentionScheduler:
    def __init__(self,
                 session_retention_days: int = 30,
                 memory_retention_days: int = 60,
                 importance_threshold: int = 0):
        self.session_retention_days = session_retention_days
        self.memory_retention_days = memory_retention_days
        self.importance_threshold = importance_threshold

    async def run(self, db: AsyncSession, dry_run: bool = True) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        session_cutoff = now - timedelta(days=self.session_retention_days)
        memory_cutoff = now - timedelta(days=self.memory_retention_days)

        # Archived sessions older than cutoff
        sess_stmt = select(Session.id).where(Session.status == "archived", Session.created_at < session_cutoff)
        sess_result = await db.execute(sess_stmt)
        session_ids_to_delete = [row[0] for row in sess_result.all()]

        # Stale memories (outside sessions to be deleted)
        mem_stmt = select(Memory.id).where(
            Memory.created_at < memory_cutoff,
            Memory.importance <= self.importance_threshold,
        )
        if session_ids_to_delete:
            mem_stmt = mem_stmt.where(~Memory.session_id.in_(session_ids_to_delete))
        mem_result = await db.execute(mem_stmt)
        memory_ids_to_delete = [row[0] for row in mem_result.all()]

        stats = {
            "dry_run": dry_run,
            "session_retention_days": self.session_retention_days,
            "memory_retention_days": self.memory_retention_days,
            "importance_threshold": self.importance_threshold,
            "sessions_identified": len(session_ids_to_delete),
            "memories_identified": len(memory_ids_to_delete),
            "sessions_deleted": 0,
            "memories_deleted": 0,
        }

        if not dry_run:
            if session_ids_to_delete:
                await db.execute(delete(Session).where(Session.id.in_(session_ids_to_delete)))
                stats["sessions_deleted"] = len(session_ids_to_delete)
            if memory_ids_to_delete:
                await db.execute(delete(Memory).where(Memory.id.in_(memory_ids_to_delete)))
                stats["memories_deleted"] = len(memory_ids_to_delete)
            await db.commit()

        return stats

__all__ = ["RetentionScheduler"]
