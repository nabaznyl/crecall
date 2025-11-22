"""
Load Testing Script for crecall API

This script uses Locust to simulate realistic user behavior and measure
performance metrics under varying load conditions.

Usage:
    # Run with web UI (default: localhost:8089)
    locust -f locustfile.py --host=http://localhost:8000

    # Run with 50 users, spawn rate 2/sec, 5 minute test
    locust -f locustfile.py --host=http://localhost:8000 -u 50 -r 2 -t 5m

    # Headless mode with CSV output
    locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 5 -t 10m --headless

Key Endpoints Tested:
  - POST /api/sessions/ (Create session)
  - GET /api/sessions/ (List sessions)
  - POST /api/clips/ (Add clip)
  - POST /api/memories/search (Search memories)
  - GET /api/memories/ (List memories)
"""

import random
import time
from datetime import datetime
from locust import HttpUser, task, between, tag
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrecallUser(HttpUser):
    """Simulates realistic user behavior on crecall API."""

    wait_time = between(0.5, 3)
    session_id = None
    memory_ids = []
    
    def on_start(self):
        """Create initial session."""
        self.create_session()
    
    def create_session(self):
        """Create a new session."""
        with self.client.post(
            "/api/sessions/",
            json={
                "name": f"Load Test {datetime.now().isoformat()}",
                "status": "active"
            },
            catch_response=True,
            name="/api/sessions/ POST"
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                self.session_id = data.get("session_id")
                response.success()
                logger.debug(f"Created session: {self.session_id}")
            else:
                response.failure(f"Failed with status {response.status_code}")
    
    @task(3)
    def list_sessions(self):
        """List all sessions."""
        with self.client.get(
            "/api/sessions/",
            catch_response=True,
            name="/api/sessions/ GET"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")
    
    @task(2)
    def get_session_details(self):
        """Get details of current session."""
        if self.session_id:
            with self.client.get(
                f"/api/sessions/{self.session_id}",
                catch_response=True,
                name="/api/sessions/{id} GET"
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed with status {response.status_code}")
    
    @task(2)
    def add_clip(self):
        """Add a clip."""
        if self.session_id:
            with self.client.post(
                "/api/clips/",
                json={
                    "session_id": self.session_id,
                    "content": f"Test clip {datetime.now().isoformat()}",
                    "is_auto": random.choice([True, False])
                },
                catch_response=True,
                name="/api/clips/ POST"
            ) as response:
                if response.status_code in [200, 201]:
                    response.success()
                else:
                    response.failure(f"Failed with status {response.status_code}")
    
    @task(4)
    def search_memories(self):
        """Search for memories."""
        query = random.choice(["memory", "test", "search", "query", "data"])
        with self.client.post(
            "/api/memories/search",
            json={
                "query": query,
                "limit": 10,
                "offset": 0
            },
            catch_response=True,
            name="/api/memories/search POST"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    self.memory_ids = [m.get("id") for m in data if m.get("id")]
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")
    
    @task(2)
    def get_memories(self):
        """List memories."""
        offset = random.randint(0, 50)
        with self.client.get(
            f"/api/memories/?limit=20&offset={offset}",
            catch_response=True,
            name="/api/memories/ GET"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Health check."""
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health GET"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")
