#!/usr/bin/env python3
import sys
import json

try:
    data = json.load(sys.stdin)
    if not data:
        print("  No clips found.")
    for clip in data:
        name = clip.get("name") or "Auto"
        clip_id = clip["clip_id"]
        db_id = clip['id']
        created = clip["created_at"].split("T")[0] + " " + clip["created_at"].split("T")[1][:8]
        print(f"  ID: {clip_id}")
        print(f"      DB ID: {db_id} | Name: {name}")
        print(f"      Created: {created}")
        if clip.get("git_branch"):
            print(f"      Branch: {clip['git_branch']}")
        print()
except Exception as e:
    print(f"Error parsing clips: {e}", file=sys.stderr)
    sys.exit(1)
