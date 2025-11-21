"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api import clips, memories, sessions
from app.services.auto_save import start_auto_save, stop_auto_save
from app.services.crash_detector import CrashDetector
from app.db.session import AsyncSessionLocal
from app.services.session_service import SessionService
from app.services.clip_service import ClipService
from app.schemas.session import SessionCreate
from app.schemas.clip import ClipCreate
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Global crash detector instance
crash_detector = CrashDetector()

app = FastAPI(
    title="crecall API",
    description="Session recall and memory management system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clips.router, prefix="/api/clips", tags=["clips"])
app.include_router(memories.router, prefix="/api/memories", tags=["memories"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "crecall API",
        "version": "0.1.0",
        "status": "active",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting crecall API...")
    
    # Check for crash from previous session
    crash_info = CrashDetector.check_for_crash()
    if crash_info:
        logger.warning("Detected crash from previous session!")
        logger.info(f"Previous session: {crash_info.get('session_id')}")
        logger.info(f"Last clip: {crash_info.get('last_clip_id')}")
        logger.info("Recovery available via 'crecall-recover' CLI")
    
    # Create session for this API instance
    session_id = f"api-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    
    async with AsyncSessionLocal() as db:
        session_service = SessionService(db)
        session = await session_service.create_session(
            SessionCreate(session_id=session_id, status="active")
        )
        
        # Create initial clip
        clip_service = ClipService(db)
        clip = await clip_service.create_clip(
            ClipCreate(
                session_id=session.id,
                content={"type": "startup", "message": "API started"},
                profile="minimal"
            )
        )
        
        # Register with crash detector
        crash_detector.register_session(session_id, str(clip.id))
        logger.info(f"Session registered: {session_id}")
    
    # Start auto-save scheduler
    await start_auto_save()
    logger.info("Auto-save scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down crecall API...")
    # Stop auto-save scheduler
    await stop_auto_save()
    logger.info("Auto-save scheduler stopped")
