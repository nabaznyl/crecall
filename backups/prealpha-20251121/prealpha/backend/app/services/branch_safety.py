"""Branch safety and divergence detection for sessions.

Analyzes recent clipped (clips) state per session to detect multiple active
branches, conflicting heads, or potentially rogue activity.
"""
from __future__ import annotations
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Session as SessionModel, Clip


class BranchSafety:
    @staticmethod
    async def analyze(db: AsyncSession, session_identifier: str) -> Dict[str, Any]:
        # Resolve session
        session_row = (
            await db.execute(select(SessionModel).where(SessionModel.session_id == session_identifier))
        ).scalar_one_or_none()
        if not session_row:
            return {"exists": False, "divergence": False, "reason": "session_not_found"}

        # Gather recent clips
        result = await db.execute(
            select(Clip).where(Clip.session_id == session_row.id).order_by(Clip.created_at.desc()).limit(200)
        )
        clips_seq = result.scalars().all()
        clips: List[Clip] = list(clips_seq)

        branch_groups: Dict[str, List[Clip]] = {}
        for c in clips:
            branch_val = getattr(c, "git_branch", None)
            branch = branch_val if isinstance(branch_val, str) and branch_val else "unknown"
            branch_groups.setdefault(branch, []).append(c)

        # Determine heads (latest per branch) and flags
        heads = {}
        for name, grp in branch_groups.items():
            head = grp[0]
            created_dt = getattr(head, "created_at", None)
            heads[name] = {
                "clip_id": head.clip_id,
                "git_commit": getattr(head, "git_commit", None),
                "dirty": bool(getattr(head, "git_dirty", False)),
                "created_at": created_dt.isoformat() if created_dt is not None else None,
            }

        divergence = len([b for b in branch_groups.keys() if b != "unknown"]) > 1
        rogue_candidates: List[str] = []
        for b, info in heads.items():
            if info["dirty"] or (b == "unknown"):
                rogue_candidates.append(b)

        # Conflicts if different branches share identical git_commit hash (likely detached head or resets)
        commit_to_branches: Dict[str, List[str]] = {}
        for b, info in heads.items():
            commit = info.get("git_commit") or ""
            if commit:
                commit_to_branches.setdefault(commit, []).append(b)
        conflicting_commits = {k: v for k, v in commit_to_branches.items() if len(v) > 1}
        if conflicting_commits:
            divergence = True

        return {
            "exists": True,
            "divergence": divergence,
            "branches": list(branch_groups.keys()),
            "counts": {b: len(grp) for b, grp in branch_groups.items()},
            "heads": heads,
            "rogue_candidates": rogue_candidates,
            "conflicting_commits": conflicting_commits,
            "suggestions": BranchSafety._suggest(divergence, rogue_candidates, conflicting_commits),
        }

    @staticmethod
    def _suggest(divergence: bool, rogues: List[str], conflicts: Dict[str, List[str]]) -> List[str]:
        s: List[str] = []
        if divergence:
            s.append("Multiple active branches detected; consider merging or isolating workspaces.")
        if rogues:
            s.append("Dirty or unknown branch state present; commit or stash changes to stabilize.")
        if conflicts:
            s.append("Identical commit on multiple branches; verify branch pointers and reflog.")
        if not s:
            s.append("No divergence indicators detected; branch topology appears healthy.")
        return s
