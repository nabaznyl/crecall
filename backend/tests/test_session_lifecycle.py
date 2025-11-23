"""
Test session lifecycle transitions (active → frozen → archived).
Uses sync TestClient for API tests, async for service layer.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.session_service import SessionService

pytestmark = pytest.mark.session_lifecycle

def test_freeze_active_session(client):
    response = client.post("/api/sessions/", json={"session_id": "test_freeze"})
    assert response.status_code in (200, 201)

    # Freeze session
    response = client.post("/api/sessions/test_freeze/freeze")
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["status"] == "frozen"
    assert data["session_id"] == "test_freeze"

    # Verify status persisted
    response = client.get("/api/sessions/test_freeze")
    assert response.status_code in (200, 201)
    assert response.json()["status"] == "frozen"


def test_freeze_frozen_session_fails(client):
    """Test freezing an already frozen session fails."""
    # Create and freeze session
    client.post("/api/sessions/", json={"session_id": "test_double_freeze"})
    client.post("/api/sessions/test_double_freeze/freeze")

    # Attempt to freeze again
    response = client.post("/api/sessions/test_double_freeze/freeze")
    assert response.status_code == 400
    assert "must be active" in response.json()["detail"]


def test_archive_frozen_session(client):
    """Test archiving a frozen session."""
    # Create, freeze session
    client.post("/api/sessions/", json={"session_id": "test_archive"})
    client.post("/api/sessions/test_archive/freeze")

    # Archive session
    response = client.post("/api/sessions/test_archive/archive")
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["status"] == "archived"
    assert data["session_id"] == "test_archive"


def test_archive_active_session_fails(client):
    """Test archiving an active session fails (must freeze first)."""
    client.post("/api/sessions/", json={"session_id": "test_direct_archive"})

    response = client.post("/api/sessions/test_direct_archive/archive")
    assert response.status_code == 400
    assert "must be frozen first" in response.json()["detail"]


def test_activate_frozen_session(client):
    """Test reactivating a frozen session."""
    # Create, freeze session
    client.post("/api/sessions/", json={"session_id": "test_activate"})
    client.post("/api/sessions/test_activate/freeze")

    # Activate session
    response = client.post("/api/sessions/test_activate/activate")
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["status"] == "active"
    assert data["session_id"] == "test_activate"


def test_activate_active_session_fails(client):
    """Test activating an already active session fails."""
    client.post("/api/sessions/", json={"session_id": "test_double_activate"})

    response = client.post("/api/sessions/test_double_activate/activate")
    assert response.status_code == 400
    assert "must be frozen" in response.json()["detail"]


def test_activate_archived_session_fails(client):
    """Test activating an archived session fails (irreversible)."""
    # Create, freeze, archive session
    client.post("/api/sessions/", json={"session_id": "test_activate_archived"})
    client.post("/api/sessions/test_activate_archived/freeze")
    client.post("/api/sessions/test_activate_archived/archive")

    # Attempt to activate archived session
    response = client.post("/api/sessions/test_activate_archived/activate")
    assert response.status_code == 400
    assert "must be frozen" in response.json()["detail"]


def test_lifecycle_complete_workflow(client):
    """Test complete lifecycle: create → freeze → archive → verify."""
    session_id = "test_lifecycle_full"

    # Create session
    response = client.post("/api/sessions/", json={"session_id": session_id})
    assert response.status_code in (200, 201)
    assert response.json()["status"] == "active"

    # Add clips (simulate enrichment)
    client.post(
        "/api/clips/",
        json={
            "session_id": session_id,
            "content": {"type": "test", "data": "clip 1"},
            "name": "Test clip 1",
        },
    )
    client.post(
        "/api/clips/",
        json={
            "session_id": session_id,
            "content": {"type": "test", "data": "clip 2"},
            "name": "Test clip 2",
        },
    )

    # Freeze session
    response = client.post(f"/api/sessions/{session_id}/freeze")
    assert response.status_code in (200, 201)
    assert response.json()["status"] == "frozen"

    # Verify summary includes clips
    response = client.get(f"/api/sessions/{session_id}/summary")
    assert response.status_code in (200, 201)
    summary = response.json()
    assert summary["status"] == "frozen"
    assert summary["clips_count"] == 2

    # Archive session
    response = client.post(f"/api/sessions/{session_id}/archive")
    assert response.status_code in (200, 201)
    assert response.json()["status"] == "archived"

    # Verify final status
    response = client.get(f"/api/sessions/{session_id}")
    assert response.status_code in (200, 201)
    assert response.json()["status"] == "archived"


@pytest.mark.asyncio
async def test_lifecycle_service_layer(db_session: AsyncSession):
    """Test lifecycle transitions via service layer directly."""
    from app.schemas.session import SessionCreate

    service = SessionService(db_session)

    # Create session
    session_data = SessionCreate(session_id="test_service_lifecycle")
    session = await service.create_session(session_data)
    assert session.status == "active"  # type: ignore[attr-defined]

    # Freeze
    frozen = await service.freeze_session("test_service_lifecycle")
    assert frozen is not None
    assert frozen.status == "frozen"  # type: ignore[attr-defined]

    # Archive
    archived = await service.archive_session("test_service_lifecycle")
    assert archived is not None
    assert archived.status == "archived"  # type: ignore[attr-defined]


def test_lifecycle_cache_invalidation(client):
    """Test cache invalidation on lifecycle transitions."""
    session_id = "test_cache_invalidation"

    # Create and fetch session (cache entry created)
    client.post("/api/sessions/", json={"session_id": session_id})
    response = client.get(f"/api/sessions/{session_id}")
    assert response.json()["status"] == "active"

    # Freeze session (should invalidate cache)
    client.post(f"/api/sessions/{session_id}/freeze")

    # Fetch again (should return updated status, not cached)
    response = client.get(f"/api/sessions/{session_id}")
    assert response.json()["status"] == "frozen"

    # Archive session
    client.post(f"/api/sessions/{session_id}/archive")

    # Verify summary cache also updated
    response = client.get(f"/api/sessions/{session_id}/summary")
    assert response.json()["status"] == "archived"


def test_lifecycle_nonexistent_session(client):
    """Test lifecycle transitions on nonexistent session return 404."""
    response = client.post("/api/sessions/nonexistent/freeze")
    assert response.status_code == 404

    response = client.post("/api/sessions/nonexistent/archive")
    assert response.status_code == 404

    response = client.post("/api/sessions/nonexistent/activate")
    assert response.status_code == 404
