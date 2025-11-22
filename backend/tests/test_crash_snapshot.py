"""Tests for crash snapshot capture and periodic scheduling."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.schemas.memory import MemoryCreate
from app.services.crash_snapshot_service import SNAPSHOT_DIR, get_crash_snapshot_service
from app.services.memory_service import MemoryService

pytestmark = pytest.mark.crash_snapshot


@pytest.mark.asyncio
async def test_crash_snapshot_capture(db_session):
    service = MemoryService(db_session)
    await service.create_memory(
        MemoryCreate(session_id="snapA", content="snapshot test", importance=1)
    )
    snap_service = get_crash_snapshot_service()
    path = await snap_service.capture_snapshot(db_session, reason="test")
    assert path.exists()
    with open(path) as f:
        data = json.load(f)
    assert data["integrity_hash"].startswith("sha256-")
    assert any(s["session_id"] == "snapA" for s in data["sessions"])


@pytest.mark.asyncio
async def test_crash_snapshot_periodic(db_session):
    service = MemoryService(db_session)
    await service.create_memory(
        MemoryCreate(session_id="snapB", content="periodic test", importance=0)
    )
    snap_service = get_crash_snapshot_service()
    first = await snap_service.ensure_periodic(db_session, interval_minutes=0)  # force immediate
    assert first is not None and first.exists()
    second = await snap_service.ensure_periodic(
        db_session, interval_minutes=120
    )  # should not create
    assert second is None
    # Simulate time passage
    snap_service._last_snapshot_at = datetime.now(timezone.utc) - timedelta(minutes=121)  # type: ignore
    third = await snap_service.ensure_periodic(db_session, interval_minutes=120)
    assert third is not None and third.exists()
