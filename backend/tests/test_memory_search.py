"""Tests for ranked memory search workflow."""

import pytest

pytestmark = pytest.mark.memory_search

from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_ranked_search_basic(db_session):
    from app.schemas.memory import MemoryCreate
    from app.services.memory_service import MemoryService

    service = MemoryService(db_session)
    # Create session implicitly via first memory
    await service.create_memory(
        MemoryCreate(
            session_id="s1", content="alpha beta gamma", tags=["t1"], category="cat", importance=1
        )
    )
    await service.create_memory(
        MemoryCreate(
            session_id="s1", content="beta gamma", tags=["t2"], category="cat", importance=0
        )
    )
    await service.create_memory(
        MemoryCreate(session_id="s1", content="gamma", tags=["t3"], category="other", importance=2)
    )

    ranked = await service.search_memories(query="beta", limit=5, session_id="s1")
    assert len(ranked) >= 2
    # Highest score should include the term more times
    scores = [r["score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_ranked_search_filters(db_session):
    from app.schemas.memory import MemoryCreate
    from app.services.memory_service import MemoryService

    service = MemoryService(db_session)
    await service.create_memory(
        MemoryCreate(
            session_id="sf", content="note apple", tags=["fruit"], category="food", importance=1
        )
    )
    await service.create_memory(
        MemoryCreate(
            session_id="sf", content="note banana", tags=["fruit"], category="food", importance=0
        )
    )
    await service.create_memory(
        MemoryCreate(
            session_id="sf", content="tool hammer", tags=["tool"], category="hardware", importance=2
        )
    )

    ranked = await service.search_memories(query="note", limit=10, category="food", session_id="sf")
    assert all(r["memory"].category == "food" for r in ranked)


@pytest.mark.asyncio
async def test_ranked_search_importance_boost(db_session):
    from app.schemas.memory import MemoryCreate
    from app.services.memory_service import MemoryService

    service = MemoryService(db_session)
    await service.create_memory(
        MemoryCreate(session_id="imp", content="focus term", tags=[], category=None, importance=0)
    )
    await service.create_memory(
        MemoryCreate(session_id="imp", content="focus term", tags=[], category=None, importance=2)
    )

    ranked = await service.search_memories(query="focus", limit=5, session_id="imp")
    assert ranked[0]["memory"].importance >= ranked[-1]["memory"].importance


@pytest.mark.asyncio
async def test_ranked_search_session_scope_isolated(db_session):
    from app.schemas.memory import MemoryCreate
    from app.services.memory_service import MemoryService

    service = MemoryService(db_session)
    await service.create_memory(
        MemoryCreate(session_id="A", content="shared term", tags=[], category=None, importance=0)
    )
    await service.create_memory(
        MemoryCreate(session_id="B", content="shared term", tags=[], category=None, importance=2)
    )

    ranked_A = await service.search_memories(query="shared", limit=5, session_id="A")
    ranked_B = await service.search_memories(query="shared", limit=5, session_id="B")
    assert all(r["memory"].session_id != ranked_B[0]["memory"].session_id for r in ranked_A)


@pytest.mark.asyncio
async def test_ranked_search_tag_filter(db_session):
    from app.schemas.memory import MemoryCreate
    from app.services.memory_service import MemoryService

    service = MemoryService(db_session)
    await service.create_memory(
        MemoryCreate(
            session_id="tags",
            content="color red",
            tags=["red", "warm"],
            category=None,
            importance=0,
        )
    )
    await service.create_memory(
        MemoryCreate(
            session_id="tags",
            content="color blue",
            tags=["blue", "cool"],
            category=None,
            importance=0,
        )
    )

    ranked = await service.search_memories(query="color", limit=10, tags=["red"], session_id="tags")
    assert any("red" in r["memory"].tags for r in ranked)
    # Ensure tag filter reduces results
    ranked_all = await service.search_memories(query="color", limit=10, session_id="tags")
    assert len(ranked) <= len(ranked_all)
