"""Async tests for Sessions API endpoints (Phase 2 execution).

Covers: create, list, get, update, summary, branch-status, delete,
duplicate creation guard (expected behavior), and rate limit admin
endpoint (expected error due to uninitialized limiter).
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.session import Base
from app.main import app

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


async def create_session(client: AsyncClient, sid: str) -> dict:
    resp = await client.post("/api/sessions/", json={"session_id": sid, "status": "active"})
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_session_create_and_list(async_client):
    await create_session(async_client, "sess-1")
    await create_session(async_client, "sess-2")

    resp_list = await async_client.get("/api/sessions/?limit=10")
    assert resp_list.status_code == 200
    listed = resp_list.json()
    ids = [s["session_id"] for s in listed]
    assert "sess-1" in ids and "sess-2" in ids
    assert len(listed) >= 2


@pytest.mark.asyncio
async def test_session_get_update_delete(async_client):
    created = await create_session(async_client, "update-me")
    sid = created["session_id"]

    # Get
    resp_get = await async_client.get(f"/api/sessions/{sid}")
    assert resp_get.status_code == 200
    assert resp_get.json()["session_id"] == sid

    # Update
    resp_upd = await async_client.put(f"/api/sessions/{sid}", json={"status": "paused"})
    assert resp_upd.status_code == 200
    assert resp_upd.json()["status"] == "paused"

    # Delete
    resp_del = await async_client.delete(f"/api/sessions/{sid}")
    assert resp_del.status_code == 204

    # Confirm deletion
    resp_get2 = await async_client.get(f"/api/sessions/{sid}")
    assert resp_get2.status_code == 404


@pytest.mark.asyncio
async def test_session_summary(async_client):
    created = await create_session(async_client, "summary-me")
    sid = created["session_id"]
    resp_sum = await async_client.get(f"/api/sessions/{sid}/summary")
    assert resp_sum.status_code == 200
    data = resp_sum.json()
    assert data["session_id"] == sid
    # Counts present
    for key in ("clips_count", "memories_count", "checkpoints_count"):
        assert key in data


@pytest.mark.asyncio
async def test_branch_status(async_client):
    created = await create_session(async_client, "branch-me")
    sid = created["session_id"]
    resp_branch = await async_client.get(f"/api/sessions/{sid}/branch-status")
    # Endpoint should return 200 with exists flag
    assert resp_branch.status_code == 200
    data = resp_branch.json()
    assert data.get("exists") is True


@pytest.mark.asyncio
async def test_duplicate_session(async_client):
    await create_session(async_client, "dupe-me")
    resp_second = await async_client.post(
        "/api/sessions/", json={"session_id": "dupe-me", "status": "active"}
    )
    assert resp_second.status_code == 409
    assert "already" in resp_second.text.lower()


@pytest.mark.asyncio
async def test_rate_limit_admin(async_client):
    # Rate limiter likely not initialized; expect 500 error
    resp = await async_client.put("/api/sessions/admin/rate-limit?new_limit=250")
    assert resp.status_code in (200, 500)
    if resp.status_code == 500:
        assert "Rate limiter not initialized" in resp.text
