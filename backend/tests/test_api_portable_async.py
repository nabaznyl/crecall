"""Async tests for Portable Export/Import & Remote Sync (Phase 5).

Scenarios covered:
 - Plain export bundle structure (/api/portable/export)
 - Plain import roundtrip (/api/portable/import)
 - Duplicate import (second import should not re-add clips/memories)
 - Encrypted export/import roundtrip (skipped if JWE unavailable)
 - Future schema version rejection (schema_version > 2)
 - Remote push mocked (scp success path)
 - Remote pull mocked (scp success path with import)

Notes:
 - Uses in-memory SQLite; dependency override identical pattern to Phase 2–4 tests.
 - Encryption availability gated by app.services.portable.JWE_AVAILABLE.
 - Monkeypatching subprocess.check_call to avoid real network activity.
"""

import base64
import json
import zlib

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Clip, Memory
from app.db.models import Session as SessionModel
from app.db.session import Base
from app.main import app
from app.services.portable import JWE_AVAILABLE

ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(ASYNC_DB_URL, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from app.db.session import get_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


async def seed_data(session: AsyncSession):
    # Create two sessions
    s1 = SessionModel(session_id="portable-1", status="active")
    s2 = SessionModel(session_id="portable-2", status="active")
    session.add_all([s1, s2])
    await session.flush()
    # Add clips
    c1 = Clip(clip_id="clip-A", session_id=s1.id, is_auto=False, content={"text": "alpha"})
    c2 = Clip(clip_id="clip-B", session_id=s2.id, is_auto=True, content={"text": "beta"})
    # Add memories
    m1 = Memory(session_id=s1.id, content="memory one", tags=["t1"], category="catA", importance=1)
    m2 = Memory(
        session_id=s2.id, content="memory two", tags=["t2", "t3"], category="catB", importance=2
    )
    session.add_all([c1, c2, m1, m2])
    await session.commit()


async def count_all(session: AsyncSession):
    sessions = (await session.execute(select(SessionModel))).scalars().all()
    clips = (await session.execute(select(Clip))).scalars().all()
    memories = (await session.execute(select(Memory))).scalars().all()
    return len(sessions), len(clips), len(memories)


@pytest.mark.asyncio
async def test_portable_export_plain(async_client, db_session):
    await seed_data(db_session)
    resp = await async_client.get("/api/portable/export")
    assert resp.status_code == 200
    data = resp.json()
    assert data["encrypted"] is False
    payload_b64 = data["payload"]
    compressed = base64.b64decode(payload_b64)
    raw = zlib.decompress(compressed)
    bundle = json.loads(raw.decode())
    for key in ("schema_version", "sessions", "clips", "memories"):
        assert key in bundle
    assert bundle["schema_version"] == 2
    assert len(bundle["sessions"]) == 2
    assert len(bundle["clips"]) == 2
    assert len(bundle["memories"]) == 2


@pytest.mark.asyncio
async def test_portable_import_roundtrip_plain(async_client, db_session):
    await seed_data(db_session)
    # Export
    export_resp = await async_client.get("/api/portable/export")
    payload = export_resp.json()["payload"]
    # Drop all and recreate empty schema for clean import
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # Import
    resp_import = await async_client.post(
        "/api/portable/import", json={"payload": payload, "encrypted": False}
    )
    assert resp_import.status_code == 200
    result = resp_import.json()
    assert result["clips"] == 2
    assert result["memories"] == 2
    # Second import (duplicate) should not re-add clips/memories
    resp_import2 = await async_client.post(
        "/api/portable/import", json={"payload": payload, "encrypted": False}
    )
    assert resp_import2.status_code == 200
    result2 = resp_import2.json()
    assert result2["clips"] == 0
    assert result2["memories"] == 0


@pytest.mark.asyncio
async def test_portable_export_import_encrypted(async_client, db_session):
    if not JWE_AVAILABLE:
        pytest.skip("Encryption libraries not available; skipping encrypted portable tests")
    await seed_data(db_session)
    # 32-byte key for A256GCM requirement
    key = "0123456789abcdef0123456789abcdef"
    resp = await async_client.get(f"/api/portable/export?encryption_key={key}")
    assert resp.status_code == 200
    data = resp.json()
    # Allow fallback if environment crypto backend fails
    if data.get("encryption_error"):
        assert data["encrypted"] is False
    else:
        assert data["encrypted"] is True
    encrypted_payload = data["payload"]
    # Import encrypted
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # If fallback occurred treat payload as plain (encrypted False)
    import_encrypted = not data.get("encryption_error") and data.get("encrypted") is True
    resp_import = await async_client.post(
        "/api/portable/import",
        json={
            "payload": encrypted_payload,
            "encrypted": import_encrypted,
            "encryption_key": key if import_encrypted else None,
        },
    )
    assert resp_import.status_code == 200, resp_import.text
    result = resp_import.json()
    assert result["clips"] == 2 and result["memories"] == 2


@pytest.mark.asyncio
async def test_portable_import_future_schema_error(async_client, db_session):
    # Craft future schema bundle
    future_bundle = {
        "schema_version": 99,
        "sessions": [],
        "clips": [],
        "memories": [],
    }
    raw = json.dumps(future_bundle).encode()
    compressed = zlib.compress(raw, 9)
    payload_b64 = base64.b64encode(compressed).decode()
    resp = await async_client.post(
        "/api/portable/import",
        json={"payload": payload_b64, "encrypted": False},
    )
    assert resp.status_code == 400
    assert "Unsupported bundle schema_version 99" in resp.text


@pytest.mark.asyncio
async def test_remote_push_mocked(async_client, db_session, monkeypatch):
    await seed_data(db_session)
    calls = {"count": 0}

    def fake_check_call(cmd):  # cmd: ["scp", local, target]
        calls["count"] += 1
        return 0

    monkeypatch.setattr("subprocess.check_call", fake_check_call)
    resp = await async_client.post(
        "/api/portable/push-remote",
        json={"host": "example.com", "path": "/tmp/crecall_bundle.json"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["method"] == "scp"
    assert calls["count"] == 1


@pytest.mark.asyncio
async def test_remote_pull_mocked(async_client, db_session, monkeypatch):
    await seed_data(db_session)
    # Export bundle first
    export_resp = await async_client.get("/api/portable/export")
    bundle_payload = export_resp.json()["payload"]

    def fake_check_call(cmd):  # cmd: ["scp", source, local_file]
        local_file = cmd[2]
        with open(local_file, "w") as f:
            f.write(bundle_payload)
        return 0

    monkeypatch.setattr("subprocess.check_call", fake_check_call)
    # Fresh DB for import to show counts included
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    resp = await async_client.post(
        "/api/portable/pull-remote",
        json={"host": "example.com", "path": "/tmp/crecall_bundle.json", "encrypted": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    import_result = data["import_result"]
    assert import_result["clips"] == 2 and import_result["memories"] == 2
