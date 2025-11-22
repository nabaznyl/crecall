"""
Application configuration settings.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "crecall"
    DEBUG: bool = True

    # API
    API_V1_STR: str = "/api"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///crecall.db"  # Default to SQLite
    POSTGRES_URL: str = ""  # Optional PostgreSQL

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Clip system
    AUTO_CLIP_INTERVAL: int = 300  # 5 minutes in seconds
    MAX_CLIPS: int = 100  # Keep last 100 clips by default
    CLIP_RETENTION_DAYS: int = 7  # Keep clips for 7 days

    # Memory system
    DEFAULT_MEMORY_LIMIT: int = 20  # Default number of memories to return

    # Phase 1 centralized config (optional, validated separately in crecall.config)
    # Tolerate these extra env vars from .env to avoid validation errors

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Phase 1: Allow extra env vars (ENVIRONMENT, LOG_LEVEL, BACKUP_DIR, DB_URL)
    )


settings = Settings()
