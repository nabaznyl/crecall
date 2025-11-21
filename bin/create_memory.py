#!/usr/bin/env python3
"""
Helper script to create memories via API from CLI.
Handles JSON construction and API calls properly.
"""

import sys
import json
import argparse
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def create_memory(content, category=None, importance=0, tags=None, session_id=None, api_url="http://localhost:8000"):
    """Create a memory via the API."""
    
    # Default session_id if not provided
    if not session_id:
        session_id = f"cli-session-{datetime.now().strftime('%Y%m%d')}"
    
    # Build payload
    payload = {
        "content": content,
        "session_id": session_id,
        "importance": importance
    }
    
    if category:
        payload["category"] = category
    
    if tags:
        # Handle both list and comma-separated string
        if isinstance(tags, str):
            payload["tags"] = [t.strip() for t in tags.split(',')]
        else:
            payload["tags"] = tags
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = Request(
            f"{api_url}/api/memories/",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except (URLError, HTTPError) as e:
        print(f"Error creating memory: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a memory via API")
    parser.add_argument("content", help="Memory content")
    parser.add_argument("--category", help="Memory category")
    parser.add_argument("--importance", type=int, default=0, choices=[0, 1, 2], help="Importance (0-2)")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--session-id", help="Session ID")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    
    args = parser.parse_args()
    
    result = create_memory(
        content=args.content,
        category=args.category,
        importance=args.importance,
        tags=args.tags,
        session_id=args.session_id,
        api_url=args.api_url
    )
    
    print(f"[crecall] Memory created: ID={result.get('id')}")
