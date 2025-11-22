"""
Clips API endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.clip import ClipCreate, ClipList, ClipResponse
from app.services.clip_service import ClipService
from app.services.retention import get_retention_manager

router = APIRouter()


@router.post("/", response_model=ClipResponse, status_code=201)
async def create_clip(clip_data: ClipCreate, db: AsyncSession = Depends(get_db)):
    """Create a new clip (manual or auto)."""
    service = ClipService(db)
    clip = await service.create_clip(clip_data)
    return clip


@router.get("/", response_model=List[ClipList])
async def list_clips(
    session_id: Optional[str] = None, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    service = ClipService(db)
    clips = await service.list_clips(session_id=session_id, limit=limit)
    return clips


@router.get("/{clip_id}", response_model=ClipResponse)
async def get_clip(clip_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific clip by ID."""
    service = ClipService(db)
    clip = await service.get_clip(clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return clip


@router.delete("/{clip_id}", status_code=204)
async def delete_clip(clip_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a clip."""
    service = ClipService(db)
    await service.delete_clip(clip_id)
    return None


@router.post("/prune")
async def prune_clips(
    keep_last: int = 100, older_than_days: Optional[int] = None, db: AsyncSession = Depends(get_db)
):
    """Prune old clips based on retention policy."""
    service = ClipService(db)
    deleted_count = await service.prune_clips(keep_last=keep_last, older_than_days=older_than_days)
    return {"deleted": deleted_count}


@router.get("/retention/stats")
async def retention_stats(session_pk: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    manager = get_retention_manager()
    return await manager.get_retention_stats(db, session_id=session_pk)


@router.post("/retention/prune")
async def retention_prune(
    session_pk: Optional[int] = None, dry_run: bool = True, db: AsyncSession = Depends(get_db)
):
    manager = get_retention_manager()
    return await manager.prune_clips(db, session_id=session_pk, dry_run=dry_run)


@router.get("/retention/config")
async def retention_get_config():
    """Get current retention configuration."""
    manager = get_retention_manager()
    return manager.get_config()


@router.put("/retention/config")
async def retention_update_config(
    clip_keep_last: Optional[int] = None,
    auto_prune_enabled: Optional[bool] = None,
    preserve_manual_clips: Optional[bool] = None,
    preserve_important_clips: Optional[bool] = None,
):
    """Update retention configuration settings."""
    manager = get_retention_manager()
    return manager.update_config(
        clip_keep_last=clip_keep_last,
        auto_prune_enabled=auto_prune_enabled,
        preserve_manual_clips=preserve_manual_clips,
        preserve_important_clips=preserve_important_clips,
    )


@router.post("/{clip_id}/restore", summary="Generate clip restoration plan")
async def restore_clip(clip_id: str, db: AsyncSession = Depends(get_db)):
    """
    Generate a structured restoration plan from a clip.
    Returns actionable steps to reconstruct environment state.
    """
    service = ClipService(db)
    clip = await service.get_clip(clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")

    # Refresh to resolve lazy-loaded attributes
    await db.refresh(clip)

    plan = {
        "clip_id": clip.clip_id,
        "clip_name": clip.name,
        "created_at": clip.created_at.isoformat() if clip.created_at is not None else None,
        "steps": [],
        "warnings": [],
    }

    # Working directory restoration
    wd = getattr(clip, "working_directory", None)
    if wd is not None and isinstance(wd, str):
        plan["steps"].append(
            {
                "type": "set_directory",
                "action": f"cd {wd}",
                "description": f"Navigate to working directory: {wd}",
            }
        )

    # Git state restoration
    branch = getattr(clip, "git_branch", None)
    commit = getattr(clip, "git_commit", None)
    dirty = getattr(clip, "git_dirty", None)

    if branch is not None and isinstance(branch, str):
        plan["steps"].append(
            {
                "type": "git_checkout",
                "action": f"git checkout {branch}",
                "description": f"Switch to branch: {branch}",
            }
        )
        if commit is not None and isinstance(commit, str):
            plan["steps"].append(
                {
                    "type": "git_reset",
                    "action": f"git reset --hard {commit}",
                    "description": f"Reset to commit: {commit[:8]}",
                }
            )
        if dirty is True:
            plan["warnings"].append("Original state had uncommitted changes; manual review needed")

    # Content restoration (clipboard, files, etc.)
    content_val = getattr(clip, "content", None)
    if content_val is not None and isinstance(content_val, dict):
        if "clipboard" in content_val:
            plan["steps"].append(
                {
                    "type": "clipboard",
                    "action": "copy_to_clipboard",
                    "data": content_val["clipboard"],
                    "description": "Restore clipboard content",
                }
            )
        if "open_files" in content_val and isinstance(content_val["open_files"], list):
            for fp in content_val["open_files"][:5]:  # Limit to 5 files
                plan["steps"].append(
                    {"type": "open_file", "action": f"open {fp}", "description": f"Open file: {fp}"}
                )
        if "active_file" in content_val:
            plan["steps"].append(
                {
                    "type": "focus_file",
                    "action": f"focus {content_val['active_file']}",
                    "description": f"Focus on: {content_val['active_file']}",
                }
            )

    plan["step_count"] = len(plan["steps"])
    plan["restorable"] = plan["step_count"] > 0

    return plan
