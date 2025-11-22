"""Security middleware: headers, rate limiting, request ID assignment, and metrics hooks."""

import time
import uuid
from typing import Awaitable, Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.cache import get_cache_manager
from app.services.metrics import metrics


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.limit = requests_per_minute
        self.cache = get_cache_manager()
        self.dynamic_limits = {"/api/metrics": 600}  # example higher limit for metrics endpoint
        self.local_counts = {}  # fallback counting when cache disabled
        # Register global instance reference for runtime updates
        global rate_limit_middleware_instance
        rate_limit_middleware_instance = self

    def set_limit(self, new_limit: int):
        self.limit = new_limit

    def set_endpoint_limit(self, path: str, limit: int):
        self.dynamic_limits[path] = limit

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        client_ip = request.client.host if request.client else "unknown"
        # Per-endpoint override
        effective_limit = self.dynamic_limits.get(request.url.path, self.limit)
        key = f"ratelimit:{client_ip}:{int(time.time() // 60)}"
        # Test harness overrides (deterministic forcing) only active in test mode
        # If CRECALL_TEST_MODE is set and header X-Force-429 present, immediately block
        # If header X-RateLimit-Override-Limit provided (int), replace effective_limit for this request
        import os

        if os.getenv("CRECALL_TEST_MODE") == "1":
            override_limit = request.headers.get("X-RateLimit-Override-Limit")
            if override_limit is not None:
                try:
                    effective_limit = int(override_limit)
                except ValueError:
                    pass  # ignore malformed, use original effective_limit
            if request.headers.get("X-Force-429") == "1":
                metrics.increment("rate_limit.block", labels={"ip": client_ip, "forced": "true"})
                return Response("Rate limit exceeded (forced)", status_code=429)
        if self.cache.enabled:
            window_count = self.cache.get(key)
            if window_count is None:
                window_count = 0
            window_count += 1
            if window_count > effective_limit:
                metrics.increment("rate_limit.block", labels={"ip": client_ip})
                return Response("Rate limit exceeded", status_code=429)
            self.cache.set(key, window_count, ttl=65)
        else:
            global rate_limit_counters
            window_count = rate_limit_counters.get(key, 0) + 1
            rate_limit_counters[key] = window_count
            if window_count > effective_limit:
                metrics.increment("rate_limit.block", labels={"ip": client_ip})
                return Response("Rate limit exceeded", status_code=429)
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        metrics.observe_latency(
            "http.request",
            elapsed_ms,
            labels={
                "path": request.url.path,
                "method": request.method,
                "status": str(response.status_code),
            },
        )
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        request_id = uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        metrics.increment(
            "http.request.count", labels={"path": request.url.path, "method": request.method}
        )
        return response


# Global mutable reference for admin updates
rate_limit_middleware_instance: Optional[RateLimitMiddleware] = None
rate_limit_counters = {}
