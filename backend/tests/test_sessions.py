"""
Unit tests for Session API endpoints
"""
import pytest


class TestSessionAPI:
    """Test session endpoints"""

    def test_create_session(self, client, sample_session_data):
        """Test creating a new session"""
        response = client.post("/api/sessions/", json=sample_session_data)
        assert response.status_code == 201
        data = response.json()
        assert data["session_id"] == sample_session_data["session_id"]
        assert data["status"] == "active"
        assert "id" in data

    def test_get_session(self, client, sample_session_data):
        """Test retrieving a session"""
        # Create session first
        create_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = create_response.json()["session_id"]

        # Get session by external session_id
        response = client.get(f"/api/sessions/{session_identifier}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == sample_session_data["session_id"]

    def test_list_sessions(self, client, sample_session_data):
        """Test listing sessions"""
        # Create multiple sessions
        client.post("/api/sessions/", json=sample_session_data)
        
        sample_session_data["session_id"] = "test-session-456"
        client.post("/api/sessions/", json=sample_session_data)

        # List sessions
        response = client.get("/api/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_update_session(self, client, sample_session_data):
        """Test updating a session"""
        # Create session
        create_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = create_response.json()["session_id"]

        # Update session using external session_id
        update_data = {"status": "paused"}
        response = client.put(f"/api/sessions/{session_identifier}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paused"

    def test_delete_session(self, client, sample_session_data):
        """Test deleting a session"""
        # Create session
        create_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = create_response.json()["session_id"]

        # Delete session using external session_id
        response = client.delete(f"/api/sessions/{session_identifier}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/sessions/{session_identifier}")
        assert get_response.status_code == 404


class TestSessionValidation:
    """Test session validation logic"""

    def test_invalid_session_data(self, client):
        """Test creating session with invalid data"""
        invalid_data = {"session_id": ""}  # Empty session_id
        response = client.post("/api/sessions/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_duplicate_session_id(self, client, sample_session_data):
        """Test creating duplicate session_id"""
        # Create first session
        client.post("/api/sessions/", json=sample_session_data)

        # Try to create duplicate
        response = client.post("/api/sessions/", json=sample_session_data)
        assert response.status_code == 409
