"""Tests for retention pruning scheduler (sessions & memories)."""
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Session, Memory
from app.services.retention_scheduler import RetentionScheduler
from app.services.memory_service import MemoryService
from app.schemas.memory import MemoryCreate

pytestmark = pytest.mark.retention_pruning

@pytest.mark.asyncio
async def test_retention_dry_run(db_session: AsyncSession):
    service = MemoryService(db_session)
    # Archived old session (2 days)
    old_time = datetime.now(timezone.utc) - timedelta(days=2)
    session_old = Session(session_id="old_archived", status="archived", created_at=old_time)
    db_session.add(session_old)
    fr = db_session.flush()
    if hasattr(fr, "__await__"):
        await fr
    # Active old session (should not delete)
    session_active = Session(session_id="active_old", status="active", created_at=old_time)
    db_session.add(session_active)
    fr = db_session.flush()
    if hasattr(fr, "__await__"):
        await fr
    # Recent archived (should not delete)
    session_recent = Session(session_id="recent_archived", status="archived")
    db_session.add(session_recent)
    fr = db_session.flush()
    if hasattr(fr, "__await__"):
        await fr
    # Stale low-importance memory (not in archived session)
    await service.create_memory(MemoryCreate(session_id="active_old", content="stale", importance=0))  # type: ignore
    # Make memory older than cutoff by manual timestamp tweak
    result = await db_session.execute(select(Memory).where(Memory.content == "stale"))
    mem_obj = result.scalar_one()
    # Direct attribute assignment for test purposes; ignore type checking
    mem_obj.created_at = datetime.now(timezone.utc) - timedelta(days=65)  # type: ignore[attr-defined]
    await db_session.commit()

    scheduler = RetentionScheduler(session_retention_days=1, memory_retention_days=60)
    stats = await scheduler.run(db_session, dry_run=True)
    assert stats["sessions_identified"] == 1  # only old_archived
    assert stats["memories_identified"] == 1  # stale memory
    assert stats["sessions_deleted"] == 0
    assert stats["memories_deleted"] == 0

@pytest.mark.asyncio
async def test_retention_execute(db_session: AsyncSession):
    service = MemoryService(db_session)
    old_time = datetime.now(timezone.utc) - timedelta(days=31)
    session_old = Session(session_id="old_archived_exec", status="archived", created_at=old_time)
    db_session.add(session_old)
    fr = db_session.flush()
    if hasattr(fr, "__await__"):
        await fr
    # Add memory inside archived session (will be deleted via cascade)
    await service.create_memory(MemoryCreate(session_id="old_archived_exec", content="m1", importance=0))  # type: ignore

    # Old low-importance memory in active session
    session_active = Session(session_id="active_for_mem", status="active", created_at=old_time)
    db_session.add(session_active)
    fr = db_session.flush()
    if hasattr(fr, "__await__"):
        await fr
    await service.create_memory(MemoryCreate(session_id="active_for_mem", content="stale2", importance=0))  # type: ignore
    result = await db_session.execute(select(Memory).where(Memory.content == "stale2"))
    mem_obj = result.scalar_one()
    mem_obj.created_at = datetime.now(timezone.utc) - timedelta(days=90)  # type: ignore[attr-defined]
    await db_session.commit()

    scheduler = RetentionScheduler(session_retention_days=30, memory_retention_days=60)
    stats = await scheduler.run(db_session, dry_run=False)
    assert stats["sessions_deleted"] == 1
    assert stats["memories_deleted"] == 1  # stale2

    # Verify deletions
    res_sess = await db_session.execute(select(Session).where(Session.session_id == "old_archived_exec"))
    assert res_sess.scalar_one_or_none() is None
    res_mem = await db_session.execute(select(Memory).where(Memory.content == "stale2"))
    assert res_mem.scalar_one_or_none() is None
