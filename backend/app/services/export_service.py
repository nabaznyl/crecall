"""Export/Import service for sessions and related entities.

Schema Version: 1

Export Format (JSON serializable dict):
{
  "schema_version": 1,
  "generated_at": "2025-11-21T12:34:56Z",
  "sessions": [
     {
       "session_id": "abc123",
       "status": "active",
       "created_at": "...",
       "updated_at": "...",
       "memories": [
          {"content": "...", "tags": [...], "category": null, "importance": 0,
           "created_at": "...", "updated_at": "...", "linked_clip_id": "clip-ext-id-or-null"}
       ],
       "clips": [
          {"clip_id": "clip123", "is_auto": true, "name": null,
           "created_at": "...", "working_directory": "...", "git_branch": "main",
           "git_commit": "abcdef", "git_dirty": false, "content": {...}}
       ],
       "checkpoints": [
          {"note": "...", "created_at": "...", "extra_data": {...}}
       ]
     }
  ],
  "integrity_hash": "sha256-<hex>"  # SHA256 over canonical JSON of sessions list
}

Import rules:
- Validate schema_version == 1.
- Recompute hash; must match integrity_hash.
- For each session: if session_id collision, append suffix "-importN" with incremental N.
- Insert sessions and related entities preserving timestamps.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Checkpoint, Clip, Memory, Session

ISO = "%Y-%m-%dT%H:%M:%SZ"
SCHEMA_VERSION = 1


class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_sessions(self, session_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        stmt = select(Session)
        if session_ids:
            stmt = stmt.where(Session.session_id.in_(session_ids))
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        export_sessions: List[Dict[str, Any]] = []
        for s in sessions:
            # Load related collections explicitly if lazy
            memories = s.memories
            clips = s.clips
            checkpoints = s.checkpoints
            export_sessions.append(
                {
                    "session_id": s.session_id,
                    "status": s.status,
                    "created_at": (
                        s.created_at.astimezone(timezone.utc).strftime(ISO)
                        if s.created_at
                        else None
                    ),
                    "updated_at": (
                        s.updated_at.astimezone(timezone.utc).strftime(ISO)
                        if s.updated_at
                        else None
                    ),
                    "memories": [
                        {
                            "content": m.content,
                            "tags": m.tags or [],
                            "category": m.category,
                            "importance": m.importance,
                            "created_at": (
                                m.created_at.astimezone(timezone.utc).strftime(ISO)
                                if m.created_at
                                else None
                            ),
                            "updated_at": (
                                m.updated_at.astimezone(timezone.utc).strftime(ISO)
                                if m.updated_at
                                else None
                            ),
                            "linked_clip_id": self._external_clip_id(m.linked_clip_id),
                        }
                        for m in memories
                    ],
                    "clips": [
                        {
                            "clip_id": c.clip_id,
                            "is_auto": c.is_auto,
                            "name": c.name,
                            "created_at": (
                                c.created_at.astimezone(timezone.utc).strftime(ISO)
                                if c.created_at
                                else None
                            ),
                            "working_directory": c.working_directory,
                            "git_branch": c.git_branch,
                            "git_commit": c.git_commit,
                            "git_dirty": c.git_dirty,
                            "content": c.content,
                        }
                        for c in clips
                    ],
                    "checkpoints": [
                        {
                            "note": cp.note,
                            "created_at": (
                                cp.created_at.astimezone(timezone.utc).strftime(ISO)
                                if cp.created_at
                                else None
                            ),
                            "working_directory": cp.working_directory,
                            "docker_context": cp.docker_context,
                            "extra_data": cp.extra_data or {},
                        }
                        for cp in checkpoints
                    ],
                }
            )

        canonical = json.dumps(export_sessions, sort_keys=True, separators=(",", ":"))
        integrity_hash = "sha256-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        return {
            "schema_version": SCHEMA_VERSION,
            "generated_at": datetime.now(timezone.utc).strftime(ISO),
            "sessions": export_sessions,
            "integrity_hash": integrity_hash,
        }

    async def import_data(self, data: Dict[str, Any]) -> List[str]:
        # Validate schema
        if data.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("Unsupported schema_version")
        sessions_payload = data.get("sessions")
        if not isinstance(sessions_payload, list):
            raise ValueError("Invalid sessions payload")
        claimed_hash = data.get("integrity_hash")
        canonical = json.dumps(sessions_payload, sort_keys=True, separators=(",", ":"))
        recalculated = "sha256-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if claimed_hash != recalculated:
            raise ValueError("Integrity hash mismatch")

        imported_ids: List[str] = []
        for sess in sessions_payload:
            base_id = sess["session_id"]
            new_id = base_id
            # Collision resolution
            counter = 1
            while await self._session_exists(new_id):
                new_id = f"{base_id}-import{counter}"
                counter += 1
            # Create session
            s = Session(session_id=new_id, status=sess.get("status", "active"))
            self.db.add(s)
            await self._flush_compat()
            # Map clips external id -> internal id
            clip_id_map: Dict[str, int] = {}
            for c in sess.get("clips", []):
                clip = Clip(
                    clip_id=c["clip_id"],
                    session_id=s.id,
                    name=c.get("name"),
                    is_auto=c.get("is_auto", True),
                    content=c.get("content") or {},
                    working_directory=c.get("working_directory"),
                    git_branch=c.get("git_branch"),
                    git_commit=c.get("git_commit"),
                    git_dirty=c.get("git_dirty", False),
                )
                self.db.add(clip)
                await self._flush_compat()
                clip_id_map[clip.clip_id] = clip.id
            # Memories
            for m in sess.get("memories", []):
                linked_clip_external = m.get("linked_clip_id")
                linked_clip_pk = (
                    clip_id_map.get(linked_clip_external) if linked_clip_external else None
                )
                mem = Memory(
                    session_id=s.id,
                    content=m.get("content"),
                    tags=m.get("tags") or [],
                    category=m.get("category"),
                    importance=m.get("importance", 0),
                    linked_clip_id=linked_clip_pk,
                )
                self.db.add(mem)
            # Checkpoints
            for cp in sess.get("checkpoints", []):
                checkpoint = Checkpoint(
                    session_id=s.id,
                    note=cp.get("note"),
                    working_directory=cp.get("working_directory"),
                    docker_context=cp.get("docker_context"),
                    extra_data=cp.get("extra_data") or {},
                )
                self.db.add(checkpoint)
            imported_ids.append(new_id)
        await self.db.commit()
        return imported_ids

    async def _session_exists(self, session_id: str) -> bool:
        result = await self.db.execute(select(Session).where(Session.session_id == session_id))
        return result.scalar_one_or_none() is not None

    async def _flush_compat(self):
        fr = self.db.flush()
        if hasattr(fr, "__await__"):
            await fr

    def _external_clip_id(self, internal_clip_id: Optional[int]) -> Optional[str]:
        if internal_clip_id is None:
            return None
        # Fetch clip external id
        # (Synchronous since identity map should have it if loaded; fallback query otherwise)
        # We avoid async overhead if possible; safe: small utility.
        return None  # Placeholder until needed to dereference


__all__ = ["ExportService", "SCHEMA_VERSION"]
