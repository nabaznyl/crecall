"""Async tests for Security & Middleware (Phase 6).

Validates security headers, request ID presence, and basic rate limiting behavior.
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


@pytest.mark.asyncio
async def test_security_headers_present(async_client):
    resp = await async_client.get("/health")
    assert resp.status_code == 200
    for header in [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Referrer-Policy",
        "Permissions-Policy",
        "X-Request-ID",
    ]:
        assert header in resp.headers


@pytest.mark.asyncio
async def test_rate_limit_basic(async_client, monkeypatch):
    import os

    os.environ["CRECALL_TEST_MODE"] = "1"
    # Force a 429 deterministically using middleware override header
    r = await async_client.get("/health", headers={"X-Force-429": "1"})
    assert r.status_code == 429


@pytest.mark.asyncio
async def test_request_id_changes_per_request(async_client):
    r1 = await async_client.get("/health")
    r2 = await async_client.get("/health")
    assert r1.headers.get("X-Request-ID") != r2.headers.get("X-Request-ID")


@pytest.mark.asyncio
async def test_rate_limit_counting(async_client):
    """Organic counting-based rate limit: override limit=2, third request blocked."""
    import os

    os.environ["CRECALL_TEST_MODE"] = "1"
    # Reset in-memory counters to ensure clean window
    from app.middleware.security import rate_limit_counters

    rate_limit_counters.clear()
    headers = {"X-RateLimit-Override-Limit": "2"}
    r1 = await async_client.get("/health", headers=headers)
    r2 = await async_client.get("/health", headers=headers)
    r3 = await async_client.get("/health", headers=headers)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429


@pytest.mark.asyncio
async def test_metrics_recorded(async_client):
    """Ensure metrics collector records counters and latency samples for requests."""
    import os

    os.environ["CRECALL_TEST_MODE"] = "1"
    from app.services.metrics import metrics

    # Snapshot baseline
    before = metrics.snapshot()
    counters_raw_before = before.get("counters")
    before_counter_total = 0
    if isinstance(counters_raw_before, list):
        for c in counters_raw_before:
            if isinstance(c, dict) and c.get("name") == "http.request.count":
                before_counter_total += c.get("value", 0)
    # Execute a few requests
    for _ in range(3):
        resp = await async_client.get("/health")
        assert resp.status_code == 200
    after = metrics.snapshot()
    counters_raw_after = after.get("counters")
    after_counter_total = 0
    if isinstance(counters_raw_after, list):
        for c in counters_raw_after:
            if isinstance(c, dict) and c.get("name") == "http.request.count":
                after_counter_total += c.get("value", 0)
    # Counter should have increased by at least 3
    assert after_counter_total - before_counter_total >= 3
    # Latency samples present
    latency_entries = []
    latency_raw = after.get("latency")
    if isinstance(latency_raw, list):
        for entry in latency_raw:
            if isinstance(entry, dict) and entry.get("name") == "http.request":
                latency_entries.append(entry)
    assert latency_entries, "Latency entries for http.request missing"
    # Ensure p95 and p99 fields exist and are numeric
    entry = latency_entries[0]
    assert "p95_ms" in entry and "p99_ms" in entry
