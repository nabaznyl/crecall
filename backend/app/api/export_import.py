"""Export / Import API endpoints for portable data bundles."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.portable import export_full, import_full
from app.services.remote_sync import RemoteSync

router = APIRouter(prefix="/api/portable", tags=["portable"])


@router.get("/export")
async def export_data(encryption_key: str | None = None, db: AsyncSession = Depends(get_db)):
    bundle = await export_full(db, encryption_key=encryption_key)
    return bundle


class ImportRequest(BaseModel):
    payload: str
    encrypted: bool = False
    encryption_key: str | None = None


class PushRemoteRequest(BaseModel):
    host: str
    user: str | None = None
    path: str = "/tmp/crecall_bundle.json"
    encryption_key: str | None = None


class PullRemoteRequest(BaseModel):
    host: str
    user: str | None = None
    path: str = "/tmp/crecall_bundle.json"
    encryption_key: str | None = None
    encrypted: bool = False


@router.post("/import")
async def import_data(request: ImportRequest, db: AsyncSession = Depends(get_db)):
    """Import a portable bundle.

    Accepts JSON body with keys: payload, encrypted, encryption_key.
    """
    try:
        result = await import_full(
            db,
            payload=request.payload,
            encrypted=request.encrypted,
            encryption_key=request.encryption_key,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {e}")


@router.post("/push-remote")
async def push_remote(request: PushRemoteRequest, db: AsyncSession = Depends(get_db)):
    """Push portable bundle to remote host (JSON body)."""
    result = await RemoteSync.push(
        db,
        host=request.host,
        user=request.user,
        path=request.path,
        encryption_key=request.encryption_key,
    )
    if result.get("status") != "ok":
        raise HTTPException(status_code=502, detail=result.get("status"))
    return result


@router.post("/pull-remote")
async def pull_remote(request: PullRemoteRequest, db: AsyncSession = Depends(get_db)):
    """Pull portable bundle from remote host and import (JSON body)."""
    result = await RemoteSync.pull(
        db,
        host=request.host,
        user=request.user,
        path=request.path,
        encryption_key=request.encryption_key,
        encrypted=request.encrypted,
    )
    if result.get("status") != "ok":
        raise HTTPException(status_code=502, detail=result.get("status"))
    return result
