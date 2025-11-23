"""Context variables for request-scoped IDs used in logging.
"""
from __future__ import annotations
from contextvars import ContextVar

# Request-scoped unique id (hex string)
request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
# Optional session identifier propagated from application session creation
session_id: ContextVar[str | None] = ContextVar("session_id", default=None)
