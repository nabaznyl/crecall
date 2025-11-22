"""
Database initialization script.
"""

import asyncio
from app.db.session import engine, Base
from app.db.models import Session, Clip, Memory, Checkpoint


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Drop all tables (caution: development only!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✓ Database initialized successfully")


if __name__ == "__main__":
    asyncio.run(init_db())
