#!/usr/bin/env python3
import sys
import json

try:
    data = json.load(sys.stdin)
    results = data.get("results", [])
    for memory in results:
        content = memory["content"]
        if len(content) > 80:
            content = content[:77] + "..."
        print(f"[{memory['id']}] {content}")
        if memory.get("category"):
            print(f"    Category: {memory['category']}")
        if memory.get("tags"):
            print(f"    Tags: {', '.join(memory['tags'])}")
        created = memory["created_at"].split("T")[0]
        print(f"    Importance: {memory['importance']} | Created: {created}")
        print()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
