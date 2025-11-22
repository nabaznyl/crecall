"""
Unit tests for Memories API endpoints
"""
import pytest


class TestMemoriesAPI:
    """Test memories endpoints"""

    def test_create_memory(self, client, sample_session_data, sample_memory_data):
        """Test creating a new memory"""
        # Create session first
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        # Create memory
        memory_data = {**sample_memory_data, "session_id": session_id}
        response = client.post("/api/memories/", json=memory_data)
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == sample_memory_data["content"]
        assert "id" in data

    def test_list_memories(self, client, sample_session_data, sample_memory_data):
        """Test listing memories"""
        # Create session and memories
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        memory_data = {**sample_memory_data, "session_id": session_id}
        client.post("/api/memories/", json=memory_data)
        
        memory_data["content"] = "Another test memory"
        client.post("/api/memories/", json=memory_data)

        # List memories
        response = client.get("/api/memories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_search_memories(self, client, sample_session_data, sample_memory_data):
        """Test searching memories"""
        # Create session and memory
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        memory_data = {**sample_memory_data, "session_id": session_id}
        client.post("/api/memories/", json=memory_data)

        # Search memories
        response = client.get("/api/memories/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any("test" in m["content"].lower() for m in data)

    def test_get_memory(self, client, sample_session_data, sample_memory_data):
        """Test retrieving a specific memory"""
        # Create session and memory
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        memory_data = {**sample_memory_data, "session_id": session_id}
        create_response = client.post("/api/memories/", json=memory_data)
        memory_id = create_response.json()["id"]

        # Get memory
        response = client.get(f"/api/memories/{memory_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == memory_id

    def test_update_memory(self, client, sample_session_data, sample_memory_data):
        """Test updating a memory"""
        # Create session and memory
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        memory_data = {**sample_memory_data, "session_id": session_id}
        create_response = client.post("/api/memories/", json=memory_data)
        memory_id = create_response.json()["id"]

        # Update memory
        update_data = {"importance": 3, "content": "Updated memory content"}
        response = client.put(f"/api/memories/{memory_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["importance"] == 3
        assert data["content"] == "Updated memory content"

    def test_delete_memory(self, client, sample_session_data, sample_memory_data):
        """Test deleting a memory"""
        # Create session and memory
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        memory_data = {**sample_memory_data, "session_id": session_id}
        create_response = client.post("/api/memories/", json=memory_data)
        memory_id = create_response.json()["id"]

        # Delete memory
        response = client.delete(f"/api/memories/{memory_id}")
        assert response.status_code == 200

        # Verify deletion
        get_response = client.get(f"/api/memories/{memory_id}")
        assert get_response.status_code == 404


class TestMemoryImportance:
    """Test memory importance filtering"""

    def test_filter_by_importance(self, client, sample_session_data):
        """Test filtering memories by importance level"""
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_id = session_response.json()["id"]

        # Create memories with different importance levels
        for importance in [1, 2, 3]:
            memory_data = {
                "session_id": session_id,
                "content": f"Memory with importance {importance}",
                "importance": importance,
                "tags": [],
                "category": "note",
            }
            client.post("/api/memories/", json=memory_data)

        # Filter high-importance memories
        response = client.get("/api/memories/?min_importance=2")
        assert response.status_code == 200
        data = response.json()
        assert all(m["importance"] >= 2 for m in data)
