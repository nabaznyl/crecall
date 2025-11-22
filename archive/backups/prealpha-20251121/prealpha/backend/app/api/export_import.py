"""Export / Import API endpoints for portable data bundles."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.portable import export_full, import_full
from app.services.remote_sync import RemoteSync

router = APIRouter(prefix="/api/portable", tags=["portable"])


@router.get("/export")
async def export_data(encryption_key: str | None = None, db: AsyncSession = Depends(get_db)):
    bundle = await export_full(db, encryption_key=encryption_key)
    return bundle


@router.post("/import")
async def import_data(payload: str, encrypted: bool = False, encryption_key: str | None = None, db: AsyncSession = Depends(get_db)):
    try:
        result = await import_full(db, payload=payload, encrypted=encrypted, encryption_key=encryption_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {e}")


@router.post("/push-remote")
async def push_remote(
    host: str,
    user: str | None = None,
    path: str = "/tmp/crecall_bundle.json",
    encryption_key: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await RemoteSync.push(db, host=host, user=user, path=path, encryption_key=encryption_key)
    if result.get("status") != "ok":
        raise HTTPException(status_code=502, detail=result.get("status"))
    return result


@router.post("/pull-remote")
async def pull_remote(
    host: str,
    user: str | None = None,
    path: str = "/tmp/crecall_bundle.json",
    encryption_key: str | None = None,
    encrypted: bool = False,
    db: AsyncSession = Depends(get_db),
):
    result = await RemoteSync.pull(db, host=host, user=user, path=path, encryption_key=encryption_key, encrypted=encrypted)
    if result.get("status") != "ok":
        raise HTTPException(status_code=502, detail=result.get("status"))
    return result
