"""Tests for export/import workflow integrity and collision handling."""

import pytest

from app.schemas.memory import MemoryCreate
from app.services.export_service import SCHEMA_VERSION, ExportService
from app.services.memory_service import MemoryService

pytestmark = pytest.mark.export_import


@pytest.mark.asyncio
async def test_export_import_roundtrip(db_session):
    mem_service = MemoryService(db_session)
    await mem_service.create_memory(
        MemoryCreate(
            session_id="sessA", content="first memory", tags=["a"], category="demo", importance=1
        )
    )
    await mem_service.create_memory(
        MemoryCreate(
            session_id="sessA", content="second memory", tags=["b"], category="demo", importance=0
        )
    )

    export_service = ExportService(db_session)
    data = await export_service.export_sessions(["sessA"])
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["sessions"]
    assert data["integrity_hash"].startswith("sha256-")

    # Import into fresh session id collision scenario
    imported = await export_service.import_data(data)
    assert len(imported) == 1
    assert imported[0].startswith("sessA")


@pytest.mark.asyncio
async def test_export_integrity_mismatch(db_session):
    mem_service = MemoryService(db_session)
    await mem_service.create_memory(
        MemoryCreate(
            session_id="sessB", content="only memory", tags=[], category=None, importance=0
        )
    )

    export_service = ExportService(db_session)
    data = await export_service.export_sessions(["sessB"])
    # Tamper with payload
    data["sessions"][0]["status"] = "tampered"
    with pytest.raises(ValueError):
        await export_service.import_data(data)


@pytest.mark.asyncio
async def test_import_session_id_collision(db_session):
    mem_service = MemoryService(db_session)
    await mem_service.create_memory(
        MemoryCreate(session_id="sessC", content="m1", tags=[], category=None, importance=0)
    )

    export_service = ExportService(db_session)
    data = await export_service.export_sessions(["sessC"])

    # Pre-create same session id to force collision
    await mem_service.create_memory(
        MemoryCreate(session_id="sessC", content="m2", tags=[], category=None, importance=1)
    )

    imported = await export_service.import_data(data)
    assert imported[0] != "sessC"
    assert imported[0].startswith("sessC-import")
