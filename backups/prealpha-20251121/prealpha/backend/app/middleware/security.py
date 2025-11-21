"""Security middleware: headers, rate limiting, request ID assignment, and metrics hooks."""
import time
import uuid
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.cache import get_cache_manager
from app.services.metrics import metrics
from typing import Optional


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
        window_count = self.cache.get(key) if self.cache.enabled else None
        if window_count is None:
            if self.cache.enabled:
                self.cache.set(key, 1, ttl=65)
        else:
            if window_count >= effective_limit:
                metrics.increment("rate_limit.block", labels={"ip": client_ip})
                return Response("Rate limit exceeded", status_code=429)
            if self.cache.enabled:
                self.cache.set(key, window_count + 1, ttl=65)
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        metrics.observe_latency("http.request", elapsed_ms, labels={"path": request.url.path, "method": request.method, "status": str(response.status_code)})
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        request_id = uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        metrics.increment("http.request.count", labels={"path": request.url.path, "method": request.method})
        return response


# Global mutable reference for admin updates
rate_limit_middleware_instance: Optional[RateLimitMiddleware] = None
