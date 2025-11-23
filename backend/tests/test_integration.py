"""
Integration tests for crecall API
"""


class TestWorkflowIntegration:
    """Test complete workflows"""

    def test_full_session_workflow(self, client):
        """Test complete session workflow: create session -> add clips -> add memories -> query"""
        # 1. Create session
        session_data = {"session_id": "workflow-test", "status": "active"}
        session_response = client.post("/api/sessions/", json=session_data)
        assert session_response.status_code == 201
        session_identifier = session_response.json()["session_id"]

        # 2. Create clips
        clip_data = {
            "session_id": session_identifier,
            "name": "initial-work",
            "is_auto": False,
            "content": {"code": "def hello(): pass", "language": "python"},
        }
        clip_response = client.post("/api/clips/", json=clip_data)
        assert clip_response.status_code == 201
        clip_id = clip_response.json()["clip_id"]

        # 3. Add memories
        memory_data = {
            "session_id": session_identifier,
            "content": "Working on hello function",
            "tags": ["python", "function"],
            "category": "note",
            "importance": 2,
            "linked_clip_id": clip_id,
        }
        memory_response = client.post("/api/memories/", json=memory_data)
        assert memory_response.status_code == 201

        # 4. Query session summary
        summary_response = client.get(f"/api/sessions/{session_identifier}/summary")
        assert summary_response.status_code == 200
        summary = summary_response.json()
        assert "clips_count" in summary or "memories_count" in summary

        # 5. Search memories (POST endpoint returns object with 'results')
        search_response = client.post("/api/memories/search?query=hello")
        assert search_response.status_code == 200
        data = search_response.json()
        assert data["count"] >= 0

    def test_clip_restore_workflow(self, client):
        """Test clip restoration workflow"""
        # Create session
        session_data = {"session_id": "restore-test", "status": "active"}
        session_response = client.post("/api/sessions/", json=session_data)
        session_identifier = session_response.json()["session_id"]

        # Create clip with state
        clip_data = {
            "session_id": session_identifier,
            "name": "checkpoint-1",
            "is_auto": False,
            "content": {
                "code": "x = 42",
                "variables": {"x": 42},
                "working_dir": "/tmp/test",
            },
        }
        clip_response = client.post("/api/clips/", json=clip_data)
        clip_id = clip_response.json()["clip_id"]

        # Restore clip (renamed from resume)
        restore_response = client.post(f"/api/clips/{clip_id}/restore")
        assert restore_response.status_code == 200

        # Verify restoration plan is returned
        plan = restore_response.json()
        assert "clip_id" in plan or "steps" in plan

    def test_context_assembly(self, client):
        """Test context assembly endpoint"""
        # Create session with clips and memories
        session_data = {"session_id": "context-test", "status": "active"}
        session_response = client.post("/api/sessions/", json=session_data)
        session_identifier = session_response.json()["session_id"]

        # Add clip
        clip_data = {
            "session_id": session_identifier,
            "name": "context-clip",
            "content": {"code": "test code"},
        }
        client.post("/api/clips/", json=clip_data)

        # Add memory
        memory_data = {
            "session_id": session_identifier,
            "content": "Important context",
            "importance": 2,
            "tags": ["context"],
            "category": "note",
        }
        client.post("/api/memories/", json=memory_data)

        # Get assembled context
        context_response = client.get("/api/context/assemble?limit_clips=5&limit_memories=5")
        assert context_response.status_code == 200
        context = context_response.json()
        assert "clips" in context or "memories" in context


class TestErrorHandling:
    """Test error handling"""

    def test_get_nonexistent_session(self, client):
        """Test getting a non-existent session"""
        response = client.get("/api/sessions/99999")
        assert response.status_code == 404

    def test_get_nonexistent_clip(self, client):
        """Test getting a non-existent clip"""
        response = client.get("/api/clips/invalid-clip-id")
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Test sending invalid JSON"""
        response = client.post(
            "/api/sessions/",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422
