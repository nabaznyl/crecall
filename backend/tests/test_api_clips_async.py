"""Async tests for Clips API endpoints (Phase 3).

These tests are aligned with the current async FastAPI implementation.
They do not alter existing synchronous tests; instead they provide
authoritative coverage for clip creation, listing, pruning, retention,
restore plan generation, and integrity flagging.
"""

from datetime import datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Clip
from app.db.session import Base
from app.main import app

# Async in-memory database setup for these tests only
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
    # Ensure signing key available for integrity verification logic
    import os
    os.environ.setdefault("CRECALL_SIGNING_KEY", "test-signing-key")

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


async def create_session_helper(
    client: AsyncClient, sid: str = "clip-test-session"
) -> tuple[str, int]:
    """Create a session and return (session_id_string, numeric_pk)."""
    resp = await client.post("/api/sessions/", json={"session_id": sid, "status": "active"})
    assert resp.status_code == 201
    data = resp.json()
    return data["session_id"], data["id"]


@pytest.mark.asyncio
async def test_clip_creation_and_listing(async_client):
    sid_str, _ = await create_session_helper(async_client)

    # Manual clip
    clip_payload = {
        "session_id": sid_str,
        "name": "manual-clip",
        "is_auto": False,
        "working_directory": "/workspace/project",
        "git_branch": "main",
        "git_commit": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        "git_dirty": True,
        "content": {
            "clipboard": "print('hello')",
            "open_files": ["README.md", "app/main.py"],
            "active_file": "app/main.py",
        },
    }
    resp_create = await async_client.post("/api/clips/", json=clip_payload)
    assert resp_create.status_code == 201
    created = resp_create.json()
    assert created["clip_id"].startswith("clip-")
    assert created["name"] == "manual-clip"
    assert created["is_auto"] is False

    # Auto clip
    auto_payload = {
        "session_id": sid_str,
        "name": "auto-clip",
        "is_auto": True,
        "content": {"clipboard": "auto", "open_files": []},
    }
    resp_auto = await async_client.post("/api/clips/", json=auto_payload)
    assert resp_auto.status_code == 201
    auto_created = resp_auto.json()
    assert auto_created["is_auto"] is True

    # List clips (unfiltered)
    resp_list = await async_client.get("/api/clips/?limit=5")
    assert resp_list.status_code == 200
    clips = resp_list.json()
    assert len(clips) >= 2
    # Ensure ordering desc by created_at
    timestamps = [datetime.fromisoformat(c["created_at"]) for c in clips]
    assert timestamps == sorted(timestamps, reverse=True)

    # Filter by session_id string
    resp_list_filtered = await async_client.get(f"/api/clips/?session_id={sid_str}&limit=5")
    assert resp_list_filtered.status_code == 200
    filtered = resp_list_filtered.json()
    assert len(filtered) >= 2


@pytest.mark.asyncio
async def test_clip_get_delete(async_client):
    sid_str, _ = await create_session_helper(async_client, sid="delete-flow")
    payload = {"session_id": sid_str, "name": "del-me", "is_auto": False, "content": {}}
    resp_create = await async_client.post("/api/clips/", json=payload)
    assert resp_create.status_code == 201
    clip_id = resp_create.json()["clip_id"]

    resp_get = await async_client.get(f"/api/clips/{clip_id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["clip_id"] == clip_id

    resp_delete = await async_client.delete(f"/api/clips/{clip_id}")
    assert resp_delete.status_code == 204

    resp_get_after = await async_client.get(f"/api/clips/{clip_id}")
    assert resp_get_after.status_code == 404


@pytest.mark.asyncio
async def test_clip_prune(async_client):
    sid_str, _ = await create_session_helper(async_client, sid="prune-flow")
    # Create 5 clips
    for i in range(5):
        payload = {"session_id": sid_str, "name": f"clip-{i}", "is_auto": True, "content": {"n": i}}
        resp = await async_client.post("/api/clips/", json=payload)
        assert resp.status_code == 201

    # Prune keep_last=3
    resp_prune = await async_client.post("/api/clips/prune?keep_last=3")
    assert resp_prune.status_code == 200
    deleted = resp_prune.json()["deleted"]
    assert deleted >= 2  # At least 2 removed

    # Verify remaining count <= 3
    resp_list = await async_client.get("/api/clips/?limit=10")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) <= 3


@pytest.mark.asyncio
async def test_retention_endpoints(async_client):
    sid_str, _ = await create_session_helper(async_client, sid="retention-flow")
    # Create clips
    for i in range(3):
        payload = {
            "session_id": sid_str,
            "name": f"rclip-{i}",
            "is_auto": True,
            "content": {"r": i},
        }
        resp = await async_client.post("/api/clips/", json=payload)
        assert resp.status_code == 201

    # Get config
    resp_cfg = await async_client.get("/api/clips/retention/config")
    assert resp_cfg.status_code == 200
    cfg_before = resp_cfg.json()
    assert "clip_keep_last" in cfg_before

    # Update config (PUT)
    resp_update = await async_client.put(
        "/api/clips/retention/config?clip_keep_last=10&auto_prune_enabled=true"
    )
    assert resp_update.status_code == 200
    cfg_after = resp_update.json()
    assert cfg_after.get("config", {}).get("clip_keep_last") == 10

    # Stats
    resp_stats = await async_client.get("/api/clips/retention/stats")
    assert resp_stats.status_code == 200
    stats = resp_stats.json()
    assert stats.get("counts", {}).get("total") >= 3

    # Dry-run prune
    resp_dry = await async_client.post("/api/clips/retention/prune?dry_run=true")
    assert resp_dry.status_code == 200
    assert resp_dry.json().get("dry_run") is True


@pytest.mark.asyncio
async def test_restore_plan(async_client):
    sid_str, _ = await create_session_helper(async_client, sid="restore-flow")
    payload = {
        "session_id": sid_str,
        "name": "restore-base",
        "is_auto": False,
        "working_directory": "/tmp/work",
        "git_branch": "feature/x",
        "git_commit": "cafebabecafebabecafebabecafebabecafebabe",
        "git_dirty": False,
        "content": {
            "clipboard": "echo restored",
            "open_files": ["main.py", "utils.py", "README.md"],
            "active_file": "utils.py",
        },
    }
    resp_create = await async_client.post("/api/clips/", json=payload)
    assert resp_create.status_code == 201
    clip_id = resp_create.json()["clip_id"]

    resp_restore = await async_client.post(f"/api/clips/{clip_id}/restore")
    assert resp_restore.status_code == 200
    plan = resp_restore.json()
    assert plan["clip_id"] == clip_id
    assert plan["step_count"] == len(plan["steps"]) and plan["step_count"] > 0
    types = {s["type"] for s in plan["steps"]}
    assert "git_checkout" in types and "clipboard" in types


@pytest.mark.asyncio
async def test_integrity_flag(async_client):
    """Force invalid integrity by manually altering stored content signature."""
    sid_str, _ = await create_session_helper(async_client, sid="integrity-flow")
    payload = {
        "session_id": sid_str,
        "name": "integrity-check",
        "is_auto": False,
        "content": {"clipboard": "data", "open_files": []},
    }
    resp_create = await async_client.post("/api/clips/", json=payload)
    assert resp_create.status_code == 201
    clip_id = resp_create.json()["clip_id"]

    # Direct DB tamper: add wrong integrity signature
    # Fetch clip row then update JSON column with mismatched signature
    async with async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )() as tamper_sess:
        result = await tamper_sess.execute(select(Clip).where(Clip.clip_id == clip_id))
        clip_obj = result.scalar_one()
        bad_content = {**clip_obj.content, "integrity": "INVALID_SIGNATURE"}
        await tamper_sess.execute(
            update(Clip).where(Clip.id == clip_obj.id).values(content=bad_content)
        )
        await tamper_sess.commit()

    resp_get = await async_client.get(f"/api/clips/{clip_id}")
    assert resp_get.status_code == 200
    data = resp_get.json()
    # When integrity invalid, service attaches integrity_status=invalid to content
    assert data["content"].get("integrity_status") == "invalid"
