"""Central configuration validation layer (Draft v0.1).
Phase: 1 (Structure)

Responsible for:
- Loading environment variables.
- Providing defaults & type conversion.
- Emitting a configuration summary.
- Future: version gating.
"""
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    environment: str
    db_url: str
    test_mode: bool
    log_level: str
    backup_dir: str

REQUIRED_VARS = ["DB_URL"]

DEFAULTS = {
    "ENVIRONMENT": "local",
    "LOG_LEVEL": "INFO",
    "BACKUP_DIR": "backups",
}

def load_config() -> AppConfig:
    missing = [v for v in REQUIRED_VARS if v not in os.environ]
    if missing:
        raise RuntimeError(f"Missing required env vars: {missing}")
    env = os.getenv("ENVIRONMENT", DEFAULTS["ENVIRONMENT"]).lower()
    db_url = os.environ["DB_URL"]
    test_mode = bool(os.getenv("CRECALL_TEST_MODE"))
    log_level = os.getenv("LOG_LEVEL", DEFAULTS["LOG_LEVEL"]).upper()
    backup_dir = os.getenv("BACKUP_DIR", DEFAULTS["BACKUP_DIR"]) 
    return AppConfig(
        environment=env,
        db_url=db_url,
        test_mode=test_mode,
        log_level=log_level,
        backup_dir=backup_dir,
    )

CONFIG = None  # lazy singleton

def get_config() -> AppConfig:
    global CONFIG
    if CONFIG is None:
        CONFIG = load_config()
    return CONFIG

if __name__ == "__main__":
    # Simple diagnostic output
    try:
        cfg = get_config()
        print("CONFIG_LOADED", cfg)
    except Exception as e:
        print("CONFIG_ERROR", e)
