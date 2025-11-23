"""Portable export/import utilities for cross-device transfer.

Supports encrypted archive generation (JSON bundle) of sessions, clips, memories.
Encryption optional: if `encryption_key` provided, a simple Fernet-like scheme
is used (requires `python-jose[cryptography]` already in requirements). Falls
back to plain JSON if encryption libs unavailable.
"""

import base64
import json
import zlib
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Clip, Memory
from app.db.models import Session as SessionModel

try:
    from jose import jwe

    JWE_AVAILABLE = True
except Exception:
    JWE_AVAILABLE = False


async def export_full(db: AsyncSession, encryption_key: str | None = None) -> dict[str, Any]:
    sessions_result = await db.execute(select(SessionModel))
    sessions = sessions_result.scalars().all()

    clips_result = await db.execute(select(Clip))
    clips = clips_result.scalars().all()

    memories_result = await db.execute(select(Memory))
    memories = memories_result.scalars().all()

    bundle = {
        "schema_version": 2,
        "generator": "crecall-backend",
        "exported_at": sessions[0].created_at.isoformat() if sessions else None,
        "sessions": [
            {
                "session_id": s.session_id,
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                "id": s.id,
            }
            for s in sessions
        ],
        "clips": [
            {
                "clip_id": c.clip_id,
                "session_pk": c.session_id,
                "is_auto": c.is_auto,
                "content": c.content,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in clips
        ],
        "memories": [
            {
                "id": m.id,
                "session_pk": m.session_id,
                "content": m.content,
                "tags": m.tags,
                "category": m.category,
                "importance": m.importance,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in memories
        ],
    }

    raw = json.dumps(bundle).encode()
    compressed = zlib.compress(raw, 9)
    if encryption_key and JWE_AVAILABLE:
        try:
            protected = jwe.encrypt(
                compressed, encryption_key, algorithm="dir", encryption="A256GCM"
            )
            return {"encrypted": True, "payload": protected}
        except Exception:
            # Fallback: return plain bundle if encryption fails (environment crypto limitations)
            return {
                "encrypted": False,
                "payload": base64.b64encode(compressed).decode(),
                "encryption_error": True,
            }
    else:
        return {"encrypted": False, "payload": base64.b64encode(compressed).decode()}


async def import_full(
    db: AsyncSession, payload: str, encrypted: bool, encryption_key: str | None = None
) -> dict[str, Any]:
    if encrypted and JWE_AVAILABLE and encryption_key:
        decompressed = jwe.decrypt(payload, encryption_key)
    else:
        decompressed = base64.b64decode(payload)
    raw = zlib.decompress(decompressed)
    data = json.loads(raw.decode())

    schema_version = data.get("schema_version", 1)
    if schema_version > 2:
        # Future-proof: unknown newer schema
        raise ValueError(f"Unsupported bundle schema_version {schema_version}")

    # Rebuild sessions map old id -> new id
    session_id_map = {}
    for s in data.get("sessions", []):
        stmt = select(SessionModel).where(SessionModel.session_id == s["session_id"])
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            session_id_map[s["id"]] = existing.id
            continue
        new_session = SessionModel(session_id=s["session_id"], status=s.get("status"))
        db.add(new_session)
        await db.flush()
        session_id_map[s["id"]] = new_session.id

    imported_clips = 0
    for c in data.get("clips", []):
        # Skip if clip_id exists
        stmt = select(Clip).where(Clip.clip_id == c["clip_id"])
        if (await db.execute(stmt)).scalar_one_or_none():
            continue
        new_clip = Clip(
            clip_id=c["clip_id"],
            session_id=session_id_map.get(c["session_pk"]),
            is_auto=c.get("is_auto", True),
            content=c.get("content"),
        )
        db.add(new_clip)
        imported_clips += 1

    imported_memories = 0
    for m in data.get("memories", []):
        stmt = select(Memory).where(
            Memory.id == m["id"]
        )  # naive duplicate check (id clash unlikely across machines)
        if (await db.execute(stmt)).scalar_one_or_none():
            continue
        new_memory = Memory(
            session_id=session_id_map.get(m["session_pk"]),
            content=m.get("content"),
            tags=m.get("tags"),
            category=m.get("category"),
            importance=m.get("importance", 1),
        )
        db.add(new_memory)
        imported_memories += 1

    await db.commit()
    return {
        "sessions": len(session_id_map),
        "clips": imported_clips,
        "memories": imported_memories,
        "encrypted": encrypted,
        "schema_version": schema_version,
    }
