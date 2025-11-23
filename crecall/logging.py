"""Structured logging initializer (Draft v0.1).
Phase: 1 (Structure)
"""
from __future__ import annotations
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from .config import get_config
try:
    # optional import, keep runtime optional
    from opentelemetry.trace import get_current_span
except Exception:  # pragma: no cover - optional
    def get_current_span():
        return None
from .log_context import request_id, session_id


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        try:
            rid = request_id.get()
            if rid:
                setattr(record, "request_id", rid)
        except Exception:
            pass
        try:
            sid = session_id.get()
            if sid:
                setattr(record, "session_id", sid)
        except Exception:
            pass
        return True

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        payload: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Optional correlation/session ID placeholder
        if hasattr(record, "session_id"):
            payload["session_id"] = getattr(record, "session_id")
        # attach trace/span ids when available
        try:
            span = get_current_span()
            if span is not None:
                ctx = span.get_span_context()
                if ctx and ctx.trace_id:
                    payload["trace_id"] = format(ctx.trace_id, '032x')
                if ctx and ctx.span_id:
                    payload["span_id"] = format(ctx.span_id, '016x')
        except Exception:
            pass
        return json.dumps(payload, ensure_ascii=False)

def init_logging() -> None:
    cfg = get_config()
    root = logging.getLogger()
    root.setLevel(getattr(logging, cfg.log_level, logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.handlers.clear()
    handler.addFilter(ContextFilter())
    root.addHandler(handler)
    logging.getLogger(__name__).debug("Logging initialized", extra={"session_id": "init"})

if __name__ == "__main__":
    init_logging()
    logging.info("test_log_line")
