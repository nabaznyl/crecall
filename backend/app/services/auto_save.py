"""
Auto-save scheduler for automatic clip creation.

This module runs as a background task and creates clips at regular intervals.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone
import asyncio
import logging
from typing import Optional

from app.core.config import settings
from app.services.clip_engine import create_clip_from_context
from app.services.clip_service import ClipService
from app.db.session import AsyncSessionLocal
from app.schemas.clip import ClipCreate

logger = logging.getLogger(__name__)


class AutoSaveScheduler:
    """Manages automatic clip creation on a schedule."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.last_clip_content: Optional[str] = None
        self.is_running = False
    
    async def create_auto_clip(self):
        """Create an automatic clip if context has changed."""
        try:
            # Capture current context
            clip_data = create_clip_from_context(profile="standard")
            
            # Simple deduplication: compare stringified content
            current_content = str(clip_data.get("git", {}))
            
            if current_content == self.last_clip_content:
                logger.info("Auto-clip skipped: No changes detected")
                return
            
            # Save clip to database
            async with AsyncSessionLocal() as db:
                service = ClipService(db)
                
                # Get or create default session
                session_id = "default-session"  # TODO: Get from context
                
                clip_create = ClipCreate(
                    session_id=session_id,
                    name=None,  # Auto-generated name
                    is_auto=True,
                    content=clip_data,
                    working_directory=clip_data.get("working_directory"),
                    git_branch=clip_data.get("git", {}).get("branch"),
                    git_commit=clip_data.get("git", {}).get("commit"),
                    git_dirty=clip_data.get("git", {}).get("dirty", False),
                )
                
                clip = await service.create_clip(clip_create)
                self.last_clip_content = current_content
                
                logger.info(f"Auto-clip created: {clip.clip_id}")
                
        except Exception as e:
            logger.error(f"Auto-clip creation failed: {e}", exc_info=True)
    
    def start(self):
        """Start the auto-save scheduler."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        # Schedule auto-clip creation
        self.scheduler.add_job(
            self.create_auto_clip,
            trigger=IntervalTrigger(seconds=settings.AUTO_CLIP_INTERVAL),
            id="auto_clip",
            name="Auto-clip creation",
            replace_existing=True,
        )
        
        self.scheduler.start()
        self.is_running = True
        
        logger.info(
            f"Auto-save scheduler started (interval: {settings.AUTO_CLIP_INTERVAL}s)"
        )
    
    def stop(self):
        """Stop the auto-save scheduler."""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Auto-save scheduler stopped")
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled auto-clip time."""
        job = self.scheduler.get_job("auto_clip")
        if job:
            return job.next_run_time
        return None


# Global scheduler instance
_scheduler: Optional[AutoSaveScheduler] = None


def get_scheduler() -> AutoSaveScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AutoSaveScheduler()
    return _scheduler


async def start_auto_save():
    """Start the auto-save system."""
    scheduler = get_scheduler()
    scheduler.start()


async def stop_auto_save():
    """Stop the auto-save system."""
    scheduler = get_scheduler()
    scheduler.stop()


if __name__ == "__main__":
    # Test the scheduler
    async def test():
        logging.basicConfig(level=logging.INFO)
        logger.info("Starting auto-save scheduler test...")
        
        await start_auto_save()
        scheduler = get_scheduler()
        
        logger.info(f"Next run: {scheduler.get_next_run_time()}")
        
        # Run for 30 seconds
        await asyncio.sleep(30)
        
        await stop_auto_save()
        logger.info("Test complete")
    
    asyncio.run(test())
