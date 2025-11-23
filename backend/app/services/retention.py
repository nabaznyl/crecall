"""
Automatic clip retention policy enforcement

Manages clip pruning based on configuration settings.
"""

import json
import logging
import os
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Clip
from app.services.metrics import metrics


class ClipRetentionManager:
    """
    Manages automatic clip pruning and retention policies.

    Features:
    - Enforces clip_keep_last configuration
    - Smart pruning (preserves important/manual clips)
    - Dry-run mode for testing
    - Statistics and reporting
    """

    def __init__(self):
        self.config_path = os.path.expanduser("~/.recall_memory/config.json")
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except Exception as e:
                logging.getLogger(__name__).warning(f"Config load error: {e}")

        return {
            "clip_keep_last": 100,
            "auto_prune_enabled": True,
            "preserve_manual_clips": True,
            "preserve_important_clips": True,
        }

    def _save_config(self) -> None:
        """Persist configuration to disk safely"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            tmp_path = self.config_path + ".tmp"
            with open(tmp_path, "w") as f:
                json.dump(self.config, f, indent=2)
            os.replace(tmp_path, self.config_path)
        except Exception as e:
            logging.getLogger(__name__).error(f"Config save error: {e}")

    def get_config(self) -> dict:
        """Return current in-memory config"""
        return self.config.copy()

    def update_config(self, **kwargs) -> dict:
        """Update retention settings and persist.
        Accepts:
        - clip_keep_last (int)
        - auto_prune_enabled (bool)
        - preserve_manual_clips (bool)
        - preserve_important_clips (bool)
        Ignores unknown keys.
        """
        allowed = {
            "clip_keep_last": int,
            "auto_prune_enabled": bool,
            "preserve_manual_clips": bool,
            "preserve_important_clips": bool,
        }
        changed = {}
        for k, v in kwargs.items():
            if k in allowed and v is not None:
                # basic type coercion/validation
                target_type = allowed[k]
                try:
                    if target_type is int:
                        v = int(v)
                    elif target_type is bool and not isinstance(v, bool):
                        if isinstance(v, str):
                            v = v.lower() in {"1", "true", "yes", "on"}
                        else:
                            v = bool(v)
                    self.config[k] = v
                    changed[k] = v
                except Exception:
                    logging.getLogger(__name__).warning(f"Invalid value for {k}: {v}")
        if changed:
            self._save_config()
        return {"updated": changed, "config": self.get_config()}

    def get_retention_limit(self) -> int:
        """Get configured retention limit"""
        return self.config.get("clip_keep_last", 100)

    def should_preserve_clip(self, clip: Clip) -> bool:
        """
        Determine if a clip should be preserved from pruning.

        Preservation rules:
        - Manual clips (is_auto=False) if preserve_manual_clips=True
        - Clips with git tags/important metadata
        - Recent clips (within last hour)
        """
        # Preserve manual clips
        is_auto_val = getattr(clip, "is_auto", True)
        if (is_auto_val is False) and self.config.get("preserve_manual_clips", True):
            return True

        # Preserve recent clips (last hour)
        created_at_val = getattr(clip, "created_at", None)
        if isinstance(created_at_val, datetime):
            if created_at_val.tzinfo is None:
                created_at_val = created_at_val.replace(tzinfo=UTC)
            if (datetime.now(UTC) - created_at_val) < timedelta(hours=1):
                return True

        # Preserve clips with important metadata
        content_val = getattr(clip, "content", None)
        if isinstance(content_val, dict):
            if content_val.get("git_tag") or content_val.get("important"):
                return True

        return False

    async def count_clips(self, db: AsyncSession, session_id: int | None = None) -> dict:
        """
        Count clips by type.

        Returns:
            Dictionary with counts {total, auto, manual, prunable}
        """
        where_clause = []
        if session_id:
            where_clause.append(Clip.session_id == session_id)
        total = (
            await db.scalar(select(func.count(Clip.id)).where(*where_clause))
            if where_clause
            else await db.scalar(select(func.count(Clip.id)))
        )
        auto = await db.scalar(
            select(func.count(Clip.id)).where(*(where_clause + [Clip.is_auto.is_(True)]))
        )
        manual = await db.scalar(
            select(func.count(Clip.id)).where(*(where_clause + [Clip.is_auto.is_(False)]))
        )
        total = total or 0
        auto = auto or 0
        manual = manual or 0

        return {
            "total": total,
            "auto": auto,
            "manual": manual,
            "prunable": total - manual if self.config.get("preserve_manual_clips") else total,
        }

    async def identify_clips_to_prune(
        self, db: AsyncSession, session_id: int | None = None, dry_run: bool = True
    ) -> list[Clip]:
        """
        Identify clips that should be pruned based on retention policy.

        Args:
            db: Database session
            session_id: Optional filter by session
            dry_run: If True, don't actually delete

        Returns:
            List of clips that would be/were pruned
        """
        retention_limit = self.get_retention_limit()

        # Get all clips ordered by creation date (newest first)
        # Select only needed columns to reduce memory footprint during pruning
        stmt = select(
            Clip.id,
            Clip.clip_id,
            Clip.session_id,
            Clip.is_auto,
            Clip.content,
            Clip.created_at,
        )
        if session_id:
            stmt = stmt.where(Clip.session_id == session_id)
        stmt = stmt.order_by(Clip.created_at.desc())
        result = await db.execute(stmt)
        rows = result.all()
        # Reconstruct lightweight clip-like objects using simple namespace pattern.
        # Use dicts instead of Clip objects for lightweight processing; adapt
        # should_preserve logic inline.
        all_clips = [
            {
                "id": r[0],
                "clip_id": r[1],
                "session_id": r[2],
                "is_auto": r[3],
                "content": r[4],
                "created_at": r[5],
            }
            for r in rows
        ]

        # Separate preserved and prunable clips
        preserved_clips = []
        prunable_clips = []

        for clip in all_clips:
            # Inline preservation logic to avoid needing full ORM instance
            preserve = False
            if (clip.get("is_auto") is False) and self.config.get("preserve_manual_clips", True):
                preserve = True
            created_at_val = clip.get("created_at")
            if not preserve and isinstance(created_at_val, datetime):
                if created_at_val.tzinfo is None:
                    created_at_val = created_at_val.replace(tzinfo=UTC)
                if (datetime.now(UTC) - created_at_val) < timedelta(hours=1):
                    preserve = True
                preserve = True
            content_val = clip.get("content")
            if not preserve and isinstance(content_val, dict):
                if content_val.get("git_tag") or content_val.get("important"):
                    preserve = True
            if preserve:
                preserved_clips.append(clip)
            else:
                prunable_clips.append(clip)

        # Calculate how many clips to remove
        total_to_keep = retention_limit
        preserved_count = len(preserved_clips)

        # If preserved clips exceed limit, we only prune prunable ones
        if preserved_count >= total_to_keep:
            # Keep all preserved, prune all prunable
            clips_to_prune = prunable_clips
        else:
            # Keep some prunable clips too
            remaining_slots = total_to_keep - preserved_count
            clips_to_prune = prunable_clips[remaining_slots:]

        return clips_to_prune

    async def prune_clips(
        self, db: AsyncSession, session_id: int | None = None, dry_run: bool = True
    ) -> dict:
        """
        Execute clip pruning based on retention policy.

        Args:
            db: Database session
            session_id: Optional filter by session
            dry_run: If True, only report what would be pruned

        Returns:
            Statistics about pruning operation
        """
        clips_to_prune = await self.identify_clips_to_prune(db, session_id, dry_run)
        counts = await self.count_clips(db, session_id)

        stats = {
            "dry_run": dry_run,
            "total_clips": counts["total"],
            "clips_identified": len(clips_to_prune),
            "clips_pruned": 0,
            "retention_limit": self.get_retention_limit(),
            "clip_ids": [clip["clip_id"] for clip in clips_to_prune],
        }

        if not dry_run and clips_to_prune:
            # Actually delete clips
            ids = [clip["id"] for clip in clips_to_prune]
            if ids:
                await db.execute(delete(Clip).where(Clip.id.in_(ids)))
                await db.commit()
            stats["clips_pruned"] = len(clips_to_prune)

        return stats

    async def auto_prune_if_needed(self, db: AsyncSession, session_id: int | None = None):
        """
        Automatically prune if clip count exceeds retention limit.

        Called after clip creation to maintain policy.
        """
        if not self.config.get("auto_prune_enabled", True):
            return

        counts = await self.count_clips(db, session_id)
        retention_limit = self.get_retention_limit()

        if counts["total"] > retention_limit * 1.1:  # 10% buffer before pruning
            logging.getLogger(__name__).info(
                f"Auto-pruning clips (total={counts['total']}, limit={retention_limit})"
            )
            result = await self.prune_clips(db, session_id, dry_run=False)
            pruned = result.get("clips_pruned", 0)
            metrics.increment("retention.prune.count", pruned)
            metrics.increment("retention.prune.events", 1)
            logging.getLogger(__name__).info(f"Pruned {pruned} clips")

    async def get_retention_stats(self, db: AsyncSession, session_id: int | None = None) -> dict:
        """
        Get detailed retention statistics.

        Useful for monitoring and dashboards.
        """
        counts = await self.count_clips(db, session_id)
        clips_to_prune = await self.identify_clips_to_prune(db, session_id, dry_run=True)

        retention_limit = self.get_retention_limit()
        usage_percent = (counts["total"] / retention_limit * 100) if retention_limit > 0 else 0
        return {
            "counts": counts,
            "retention_limit": retention_limit,
            "usage_percent": round(usage_percent, 2),
            "clips_over_limit": max(0, counts["total"] - retention_limit),
            "clips_to_prune": len(clips_to_prune),
            "auto_prune_enabled": self.config.get("auto_prune_enabled", True),
            "preserve_manual": self.config.get("preserve_manual_clips", True),
            "health": (
                "good" if usage_percent < 90 else "warning" if usage_percent < 110 else "critical"
            ),
        }


# Global instance
_retention_manager = None


def get_retention_manager() -> ClipRetentionManager:
    """Get or create the global retention manager"""
    global _retention_manager

    if _retention_manager is None:
        _retention_manager = ClipRetentionManager()

    return _retention_manager
