"""Async tests for Memories API endpoints (Phase 4).

Covers create, list with filters, get/update/delete, advanced search,
categories, popular tags, importance and date filtering.
"""

from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Memory
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


async def create_memory(client: AsyncClient, session_identifier: str, **overrides) -> dict:
    payload = {
        "session_id": session_identifier,
        "content": overrides.get("content", "Memory content"),
        "tags": overrides.get("tags", ["alpha"]),
        "category": overrides.get("category", "note"),
        "importance": overrides.get("importance", 0),
    }
    resp = await client.post("/api/memories/", json=payload)
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_memory_create_and_list(async_client):
    m1 = await create_memory(async_client, "sess-A", content="First", tags=["t1"], category="cat1")
    m2 = await create_memory(async_client, "sess-A", content="Second", tags=["t2"], category="cat2")
    m3 = await create_memory(async_client, "sess-B", content="Third", tags=["t3"], category="cat2")

    # List all
    resp_all = await async_client.get("/api/memories/?limit=10")
    assert resp_all.status_code == 200
    all_list = resp_all.json()
    assert len(all_list) >= 3
    # Ensure ordering desc by created_at
    times = [datetime.fromisoformat(m["created_at"]) for m in all_list]
    assert times == sorted(times, reverse=True)

    # Filter by session_id sess-A
    resp_sess = await async_client.get("/api/memories/?session_id=sess-A&limit=10")
    data_sess = resp_sess.json()
    ids_session = {m["id"] for m in data_sess}
    assert m1["id"] in ids_session and m2["id"] in ids_session
    assert m3["id"] not in ids_session


@pytest.mark.asyncio
async def test_memory_get_update_delete(async_client):
    created = await create_memory(
        async_client, "sess-X", content="Original", tags=["edit"], importance=1
    )
    mid = created["id"]

    # Get
    resp_get = await async_client.get(f"/api/memories/{mid}")
    assert resp_get.status_code == 200
    assert resp_get.json()["content"] == "Original"

    # Update
    resp_upd = await async_client.put(
        f"/api/memories/{mid}",
        json={"content": "Updated", "importance": 2, "tags": ["edit", "updated"]},
    )
    assert resp_upd.status_code == 200
    upd = resp_upd.json()
    assert upd["content"] == "Updated"
    assert upd["importance"] == 2
    assert "updated" in upd["tags"]

    # Delete
    resp_del = await async_client.delete(f"/api/memories/{mid}")
    assert resp_del.status_code == 204
    resp_get2 = await async_client.get(f"/api/memories/{mid}")
    assert resp_get2.status_code == 404


@pytest.mark.asyncio
async def test_memory_advanced_search(async_client):
    # Create memories with varied attributes
    await create_memory(
        async_client,
        "sess-S",
        content="Search apple",
        tags=["fruit"],
        category="food",
        importance=1,
    )
    await create_memory(
        async_client,
        "sess-S",
        content="Search banana",
        tags=["fruit", "yellow"],
        category="food",
        importance=2,
    )
    await create_memory(
        async_client, "sess-S", content="Search carrot", tags=["veg"], category="food", importance=0
    )

    resp_search = await async_client.post(
        "/api/memories/search?query=Search&min_importance=1&limit=10"
    )
    assert resp_search.status_code == 200
    data = resp_search.json()
    assert data["count"] >= 2
    # Ensure importance ordering (desc then created_at desc inside service logic)
    imps = [m["memory"]["importance"] for m in data["results"]]
    assert imps == sorted(imps, reverse=True)


@pytest.mark.asyncio
async def test_categories_endpoint(async_client):
    await create_memory(async_client, "sess-C", category="catA")
    await create_memory(async_client, "sess-C", category="catB")
    await create_memory(async_client, "sess-C", category="catA")
    resp_cat = await async_client.get("/api/memories/categories")
    assert resp_cat.status_code == 200
    cats = resp_cat.json()["categories"]
    assert "catA" in cats and "catB" in cats


@pytest.mark.asyncio
async def test_popular_tags_endpoint(async_client):
    await create_memory(async_client, "sess-T", tags=["x", "y"])
    await create_memory(async_client, "sess-T", tags=["x", "z"])
    await create_memory(async_client, "sess-T", tags=["x"])
    resp_tags = await async_client.get("/api/memories/tags/popular?limit=5")
    assert resp_tags.status_code == 200
    tags = resp_tags.json()["tags"]
    # Expect tag x count >= 3
    tag_x = next((t for t in tags if t["tag"] == "x"), None)
    assert tag_x and tag_x["count"] >= 3


@pytest.mark.asyncio
async def test_importance_and_date_filters(async_client):
    now = datetime.now(UTC)
    m_old = await create_memory(async_client, "sess-D", content="Old", importance=0)
    # Simulate older timestamp by direct DB update
    async with async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )() as raw_sess:
        result = await raw_sess.execute(select(Memory).where(Memory.id == m_old["id"]))
        obj = result.scalar_one()
        obj.created_at = now - timedelta(days=2)
        await raw_sess.commit()

    await create_memory(async_client, "sess-D", content="Important recent", importance=2)

    # Use naive ISO (strip timezone) to match existing endpoint parser expectations
    date_from = (now - timedelta(days=1)).replace(tzinfo=None).isoformat()
    resp_search = await async_client.post(
        f"/api/memories/search?query=&min_importance=1&date_from={date_from}&limit=10"
    )
    assert resp_search.status_code == 200
    data = resp_search.json()
    # Only recent important memory should appear
    contents = [m["memory"]["content"] for m in data["results"]]
    assert "Important recent" in contents and "Old" not in contents
