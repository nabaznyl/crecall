#!/usr/bin/env python3
"""
Test script for API endpoints - Sessions
Phase 2 of pre-alpha testing
"""
try:
    import httpx as requests
except ImportError:
    import sys

    print("httpx not installed. Install with: pip install httpx")
    sys.exit(1)

import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


def print_test(name, status="RUN"):
    icons = {"RUN": "🔵", "PASS": "✅", "FAIL": "❌", "SKIP": "⚠️"}
    print(f"{icons.get(status, '•')} {name}")


def test_create_session():
    print_test("POST /api/sessions/ - Create session")
    try:
        response = requests.post(
            f"{API_URL}/sessions/",
            json={"session_id": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"},
            timeout=5,
        )
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            session_id_str = data.get("session_id")
            print(f"  Created: {session_id_str} (ID: {data.get('id')})")
            print_test("POST /api/sessions/", "PASS")
            return session_id_str  # Return session_id string for subsequent tests
        else:
            print(f"  Status: {response.status_code}")
            print_test("POST /api/sessions/", "FAIL")
            return None
    except (requests.ConnectError, requests.TimeoutException):
        print("  Server not running")
        print_test("POST /api/sessions", "SKIP")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        print_test("POST /api/sessions", "FAIL")
        return None


def test_list_sessions():
    print_test("GET /api/sessions/ - List sessions")
    try:
        response = requests.get(f"{API_URL}/sessions/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {len(data)} sessions")
            print_test("GET /api/sessions", "PASS")
            return True
        else:
            print(f"  Status: {response.status_code}")
            print_test("GET /api/sessions", "FAIL")
            return False
    except (requests.ConnectError, requests.TimeoutException):
        print("  Server not running")
        print_test("GET /api/sessions", "SKIP")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        print_test("GET /api/sessions", "FAIL")
        return False


def test_get_session(sample_session_data):
    session_id = sample_session_data.get("session_id", "test-session")
    print_test(f"GET /api/sessions/{session_id} - Get single session")
    try:
        response = requests.get(f"{API_URL}/sessions/{session_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  Session: {data.get('session_id')}, Status: {data.get('status')}")
            print_test(f"GET /api/sessions/{session_id}", "PASS")
            return True
        elif response.status_code == 404:
            print("  Not found")
            print_test(f"GET /api/sessions/{session_id}", "FAIL")
            return False
        else:
            print(f"  Status: {response.status_code}")
            print_test(f"GET /api/sessions/{session_id}", "FAIL")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        print_test(f"GET /api/sessions/{session_id}", "SKIP")
        return False


def test_update_session(sample_session_data):
    session_id = sample_session_data.get("session_id", "test-session")
    print_test(f"PUT /api/sessions/{session_id} - Update session")
    try:
        response = requests.put(
            f"{API_URL}/sessions/{session_id}", json={"status": "paused"}, timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Updated status: {data.get('status')}")
            print_test(f"PUT /api/sessions/{session_id}", "PASS")
            return True
        else:
            print(f"  Status: {response.status_code}")
            print_test(f"PUT /api/sessions/{session_id}", "FAIL")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        print_test(f"PUT /api/sessions/{session_id}", "SKIP")
        return False


def test_branch_status(sample_session_data):
    session_id = sample_session_data.get("session_id", "test-session")
    print_test(f"GET /api/sessions/{session_id}/branch-status - Branch safety")
    try:
        response = requests.get(f"{API_URL}/sessions/{session_id}/branch-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  Status: {data.get('status', 'unknown')}")
            print_test(f"GET /api/sessions/{session_id}/branch-status", "PASS")
            return True
        else:
            print(f"  Status: {response.status_code}")
            print_test(f"GET /api/sessions/{session_id}/branch-status", "FAIL")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        print_test(f"GET /api/sessions/{session_id}/branch-status", "SKIP")
        return False


def test_rate_limit_admin():
    print_test("PUT /api/sessions/admin/rate-limit - Dynamic rate limit")
    try:
        response = requests.put(
            f"{API_URL}/sessions/admin/rate-limit", params={"new_limit": 200}, timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Updated limit: {data.get('effective_limit')}")
            print_test("PUT /api/admin/rate-limit", "PASS")
            return True
        else:
            print(f"  Status: {response.status_code}")
            print_test("PUT /api/admin/rate-limit", "FAIL")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        print_test("PUT /api/admin/rate-limit", "SKIP")
        return False


def test_delete_session(sample_session_data):
    session_id = sample_session_data.get("session_id", "test-session")
    print_test(f"DELETE /api/sessions/{session_id} - Delete session")
    try:
        response = requests.delete(f"{API_URL}/sessions/{session_id}", timeout=5)
        if response.status_code == 204:
            print("  Deleted successfully")
            print_test(f"DELETE /api/sessions/{session_id}", "PASS")
            return True
        else:
            print(f"  Status: {response.status_code}")
            print_test(f"DELETE /api/sessions/{session_id}", "FAIL")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        print_test(f"DELETE /api/sessions/{session_id}", "SKIP")
        return False


def main():
    print("=" * 60)
    print("API Endpoint Tests - Sessions (Phase 2)")
    print("=" * 60)
    print()

    # Test sequence
    test_list_sessions()
    session_id = test_create_session()

    if session_id:
        test_get_session(session_id)
        test_update_session(session_id)
        test_branch_status(session_id)
        test_delete_session(session_id)

    test_rate_limit_admin()

    print()
    print("=" * 60)
    print("Test run complete. Check results above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
