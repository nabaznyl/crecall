"""
Unit tests for Clips API endpoints
"""
import pytest


class TestClipsAPI:
    """Test clips endpoints"""

    def test_create_clip(self, client, sample_session_data, sample_clip_data):
        """Test creating a new clip"""
        # Create session first
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        # Create clip
        clip_data = {**sample_clip_data, "session_id": session_id}
        response = client.post("/api/clips/", json=clip_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_clip_data["name"]
        assert "clip_id" in data

    def test_list_clips(self, client, sample_session_data, sample_clip_data):
        """Test listing clips"""
        # Create session and clips
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        clip_data = {**sample_clip_data, "session_id": session_id}
        client.post("/api/clips/", json=clip_data)
        
        clip_data["name"] = "test-clip-2"
        client.post("/api/clips/", json=clip_data)

        # List clips
        response = client.get("/api/clips/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_clip(self, client, sample_session_data, sample_clip_data):
        """Test retrieving a specific clip"""
        # Create session and clip
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        clip_data = {**sample_clip_data, "session_id": session_id}
        create_response = client.post("/api/clips/", json=clip_data)
        clip_id = create_response.json()["clip_id"]

        # Get clip
        response = client.get(f"/api/clips/{clip_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["clip_id"] == clip_id

    def test_resume_clip(self, client, sample_session_data, sample_clip_data):
        """Test resuming from a clip"""
        # Create session and clip
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        clip_data = {**sample_clip_data, "session_id": session_id}
        create_response = client.post("/api/clips/", json=clip_data)
        clip_id = create_response.json()["clip_id"]

        # Resume clip
        response = client.post(f"/api/clips/{clip_id}/resume")
        assert response.status_code == 200

    def test_delete_clip(self, client, sample_session_data, sample_clip_data):
        """Test deleting a clip"""
        # Create session and clip
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        clip_data = {**sample_clip_data, "session_id": session_id}
        create_response = client.post("/api/clips/", json=clip_data)
        clip_id = create_response.json()["clip_id"]

        # Delete clip
        response = client.delete(f"/api/clips/{clip_id}")
        assert response.status_code == 200

        # Verify deletion
        get_response = client.get(f"/api/clips/{clip_id}")
        assert get_response.status_code == 404


class TestAutoClips:
    """Test auto-clip functionality"""

    def test_create_auto_clip(self, client, sample_session_data):
        """Test creating an auto-clip"""
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        clip_data = {
            "session_id": session_id,
            "name": "auto-clip",
            "is_auto": True,
            "content": {"code": "auto-saved code"},
        }

        response = client.post("/api/clips/", json=clip_data)
        assert response.status_code == 200
        data = response.json()
        assert data["is_auto"] is True
