"""Crash snapshot service.

Creates integrity-protected export snapshots of all sessions+related data
on demand (manual trigger) or periodically.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.export_service import ExportService

SNAPSHOT_DIR = Path.home() / ".recall_memory" / "snapshots"
ISO = "%Y-%m-%dT%H-%M-%S"

class CrashSnapshotService:
    def __init__(self):
        self._last_snapshot_at: Optional[datetime] = None

    async def capture_snapshot(self, db: AsyncSession, reason: str = "manual", session_ids: Optional[list[str]] = None) -> Path:
        """Capture a snapshot and persist to filesystem.

        File name pattern: snapshot-<timestamp>-<reason>.json
        Returns path to written snapshot file.
        """
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc)
        fname = f"snapshot-{ts.strftime(ISO)}-{reason}.json"
        path = SNAPSHOT_DIR / fname
        exporter = ExportService(db)
        data = await exporter.export_sessions(session_ids)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        self._last_snapshot_at = ts
        return path

    async def ensure_periodic(self, db: AsyncSession, interval_minutes: int = 30) -> Optional[Path]:
        """Capture snapshot if interval since last snapshot exceeded.
        Returns path if new snapshot created else None.
        """
        now = datetime.now(timezone.utc)
        if self._last_snapshot_at is None or (now - self._last_snapshot_at) >= timedelta(minutes=interval_minutes):
            return await self.capture_snapshot(db, reason="periodic")
        return None

# Global instance
_snapshot_service: Optional[CrashSnapshotService] = None

def get_crash_snapshot_service() -> CrashSnapshotService:
    global _snapshot_service
    if _snapshot_service is None:
        _snapshot_service = CrashSnapshotService()
    return _snapshot_service

__all__ = ["CrashSnapshotService", "get_crash_snapshot_service"]
