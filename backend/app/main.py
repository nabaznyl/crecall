"""
Main FastAPI application entry point.
"""

import logging
import os
import sys

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Phase 1: Centralized config & logging initialization
# Add parent crecall package to path for config/logging modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from crecall.config import get_config
    from crecall.logging import init_logging

    # Initialize structured logging early
    os.environ.setdefault("DB_URL", "sqlite+aiosqlite:///./crecall.db")  # Fallback for tests
    init_logging()
    _app_config = get_config()
    logger = logging.getLogger(__name__)
    logger.info("Centralized config loaded", extra={"environment": _app_config.environment})
except Exception as e:
    # Fallback to basic logging if centralized config unavailable
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Centralized config/logging unavailable: {e}")

import uuid
from datetime import UTC, datetime

from fastapi import Response

from app.api import clipped as clipped_router
from app.api import clips, context_router, export_import, memories, sessions
from app.core.config import settings
from app.db.session import AsyncSessionLocal, Base, engine
from app.middleware.security import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)
from app.schemas.clip import ClipCreate
from app.schemas.session import SessionCreate
from app.services.auto_save import start_auto_save, stop_auto_save
from app.services.clip_service import ClipService
from app.services.crash_detector import CrashDetector
from app.services.metrics import metrics
from app.services.session_service import SessionService

# Global crash detector instance
crash_detector = CrashDetector()

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting crecall API (lifespan)...")
    crash_info = CrashDetector.check_for_crash()
    if crash_info:
        logger.warning("Detected crash from previous session!")
        logger.info(f"Previous session: {crash_info.get('session_id')}")
        logger.info(f"Last clip: {crash_info.get('last_clip_id')}")
        logger.info("Recovery available via 'crecall-recover' CLI")

    # Ensure schema exists (covers in-memory / first run)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error(f"Schema initialization failed: {e}")

    # Create session + initial clip
    session_id = (
        f"api-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    )
    async with AsyncSessionLocal() as db:
        session_service = SessionService(db)
        session = await session_service.create_session(
            SessionCreate(session_id=session_id, status="active")
        )
        clip_service = ClipService(db)
        clip = await clip_service.create_clip(
            ClipCreate(
                session_id=session.session_id,  # Use external session_id (string), not internal PK
                content={"type": "startup", "message": "API started"},
                profile="minimal",
            )
        )
        crash_detector.register_session(session_id, str(clip.id))
        logger.info(f"Session registered: {session_id}")

    await start_auto_save()
    logger.info("Auto-save scheduler started")
    try:
        yield
    finally:
        logger.info("Shutting down crecall API (lifespan)...")
        await stop_auto_save()
        logger.info("Auto-save scheduler stopped")


app = FastAPI(
    title="crecall API",
    description="Session recall and memory management system",
    version="0.1.0d-7",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware stack
rate_limit_middleware = RateLimitMiddleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(rate_limit_middleware)

# Include routers
app.include_router(clips.router, prefix="/api/clips", tags=["clips"])
app.include_router(clipped_router.router, prefix="/api/clipped", tags=["clipped"])
app.include_router(memories.router, prefix="/api/memories", tags=["memories"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(context_router, prefix="/api/context", tags=["context"])
app.include_router(export_import.router)

# Documentation / OpenAPI router additions
docs_router = APIRouter()


@docs_router.get("/openapi.json", include_in_schema=False)
async def openapi_json():
    """Return the live OpenAPI schema (for packaging/export)."""
    return JSONResponse(app.openapi())


@docs_router.get("/docs/ping", include_in_schema=False)
async def docs_ping():  # simple health for docs packaging
    return {"ok": True}


app.include_router(docs_router)

# Metrics endpoint (read-only)
metrics_router = APIRouter()


@metrics_router.get("/api/metrics", tags=["system"], summary="System metrics snapshot")
async def metrics_snapshot():
    return metrics.snapshot()


@metrics_router.get("/metrics/prom", include_in_schema=False)
async def metrics_prom():
    return Response(metrics.prometheus(), media_type="text/plain; version=0.0.4")


app.include_router(metrics_router)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "crecall API",
        "version": "0.1.0d-7",
        "status": "active",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


## Deprecated startup/shutdown events replaced by lifespan above.
