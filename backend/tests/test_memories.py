"""
Unit tests for Memories API endpoints (legacy sync - updated to match current API contract)
"""



class TestMemoriesAPI:
    """Test memories endpoints"""

    def test_create_memory(self, client, sample_session_data, sample_memory_data):
        """Test creating a new memory"""
        # Create session first
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = session_response.json()["session_id"]

        # Create memory (uses external session_id string)
        memory_data = {**sample_memory_data, "session_id": session_identifier}
        response = client.post("/api/memories/", json=memory_data)
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == sample_memory_data["content"]
        assert "id" in data

    def test_list_memories(self, client, sample_session_data, sample_memory_data):
        """Test listing memories"""
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = session_response.json()["session_id"]

        memory_data = {**sample_memory_data, "session_id": session_identifier}
        client.post("/api/memories/", json=memory_data)

        memory_data["content"] = "Another test memory"
        client.post("/api/memories/", json=memory_data)

        response = client.get("/api/memories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_search_memories(self, client, sample_session_data, sample_memory_data):
        """Test searching memories (updated endpoint: POST /search returns object)"""
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = session_response.json()["session_id"]

        memory_data = {**sample_memory_data, "session_id": session_identifier}
        client.post("/api/memories/", json=memory_data)

        response = client.post("/api/memories/search?query=test")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        # Results now wrap memory object with score; access nested structure
        assert any("test" in result["memory"]["content"].lower() for result in data["results"])

    def test_get_memory(self, client, sample_session_data, sample_memory_data):
        """Test retrieving a specific memory"""
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = session_response.json()["session_id"]

        memory_data = {**sample_memory_data, "session_id": session_identifier}
        create_response = client.post("/api/memories/", json=memory_data)
        memory_id = create_response.json()["id"]

        response = client.get(f"/api/memories/{memory_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == memory_id

    def test_update_memory(self, client, sample_session_data, sample_memory_data):
        """Test updating a memory (importance max 2)"""
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = session_response.json()["session_id"]

        memory_data = {**sample_memory_data, "session_id": session_identifier}
        create_response = client.post("/api/memories/", json=memory_data)
        memory_id = create_response.json()["id"]

        update_data = {"importance": 2, "content": "Updated memory content"}
        response = client.put(f"/api/memories/{memory_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["importance"] == 2
        assert data["content"] == "Updated memory content"

    def test_delete_memory(self, client, sample_session_data, sample_memory_data):
        """Test deleting a memory (expects 204)"""
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = session_response.json()["session_id"]

        memory_data = {**sample_memory_data, "session_id": session_identifier}
        create_response = client.post("/api/memories/", json=memory_data)
        memory_id = create_response.json()["id"]

        response = client.delete(f"/api/memories/{memory_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/memories/{memory_id}")
        assert get_response.status_code == 404


class TestMemoryImportance:
    """Test memory importance filtering (uses search endpoint)"""

    def test_filter_by_importance(self, client, sample_session_data):
        session_response = client.post("/api/sessions/", json=sample_session_data)
        session_identifier = session_response.json()["session_id"]

        # Create memories within valid importance range 0-2
        for importance in [0, 1, 2]:
            memory_data = {
                "session_id": session_identifier,
                "content": f"Memory with importance {importance}",
                "importance": importance,
                "tags": [],
                "category": "note",
            }
            resp = client.post("/api/memories/", json=memory_data)
            assert resp.status_code == 201

        # Filter high-importance memories via search endpoint
        response = client.post("/api/memories/search?query=&min_importance=1")
        assert response.status_code == 200
        data = response.json()
        # Results wrap memory object with score; access nested structure
        assert all(result["memory"]["importance"] >= 1 for result in data["results"])
