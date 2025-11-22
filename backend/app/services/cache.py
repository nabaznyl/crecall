"""
Redis caching layer for performance optimization

Provides caching for:
- Session data
- Query results
- Embeddings
- Frequently accessed memories
"""

import hashlib
import json
import os
import pickle
from functools import wraps
from typing import Any, List, Optional

try:
    import redis  # type: ignore[import-not-found]

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheManager:
    """
    Redis-based caching manager with fallback to memory cache.

    Features:
    - Automatic TTL management
    - Query result caching
    - Embedding cache
    - Session data cache
    """

    def __init__(self):
        """Initialize cache manager"""
        self.enabled = os.getenv("CRECALL_ENABLE_CACHE", "0") == "1"
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache

        if self.enabled and REDIS_AVAILABLE:
            self._connect_redis()
        elif self.enabled:
            print("⚠ Redis not installed. Using in-memory cache.")
            print("  Install: pip install redis")

    def _connect_redis(self):
        """Connect to Redis server"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            self.redis_client.ping()
            print(f"✓ Connected to Redis at {redis_url}")
        except Exception as e:
            print(f"⚠ Redis connection failed: {e}")
            print("  Falling back to in-memory cache")
            self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.enabled:
            return None

        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
            except Exception as e:
                print(f"Cache get error: {e}")
                return None
        else:
            return self.memory_cache.get(key)

    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default 1 hour)
        """
        if not self.enabled:
            return

        if self.redis_client:
            try:
                serialized = pickle.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
            except Exception as e:
                print(f"Cache set error: {e}")
        else:
            self.memory_cache[key] = value

    def delete(self, key: str):
        """Delete key from cache"""
        if not self.enabled:
            return

        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"Cache delete error: {e}")
        else:
            self.memory_cache.pop(key, None)

    def clear(self):
        """Clear all cache"""
        if not self.enabled:
            return

        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                print(f"Cache clear error: {e}")
        else:
            self.memory_cache.clear()

    def cache_query_result(self, query_hash: str, result: Any, ttl: int = 300):
        """Cache database query result"""
        key = f"query:{query_hash}"
        self.set(key, result, ttl)

    def get_cached_query(self, query_hash: str) -> Optional[Any]:
        """Get cached query result"""
        key = f"query:{query_hash}"
        return self.get(key)

    def cache_embedding(self, text: str, embedding: Any, ttl: int = 86400):
        """Cache text embedding (24 hour TTL)"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        key = f"embedding:{text_hash}"
        self.set(key, embedding, ttl)

    def get_cached_embedding(self, text: str) -> Optional[Any]:
        """Get cached embedding"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        key = f"embedding:{text_hash}"
        return self.get(key)

    def cache_session(self, session_id: int, session_data: dict, ttl: int = 1800):
        """Cache session data (30 minute TTL)"""
        key = f"session:{session_id}"
        self.set(key, session_data, ttl)

    def get_cached_session(self, session_id: int) -> Optional[dict]:
        """Get cached session data"""
        key = f"session:{session_id}"
        return self.get(key)

    def invalidate_session(self, session_id: int):
        """Invalidate session cache"""
        key = f"session:{session_id}"
        self.delete(key)


# Global instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get or create the global cache manager instance"""
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager()

    return _cache_manager


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function results.

    Usage:
        @cached(ttl=600, key_prefix="memories")
        def expensive_function(arg1, arg2):
            # expensive operation
            return result

    Args:
        ttl: Cache time-to-live in seconds
        key_prefix: Prefix for cache key
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            if not cache.enabled:
                return func(*args, **kwargs)

            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key_hash = hashlib.md5(cache_key.encode()).hexdigest()

            # Try to get from cache
            cached_result = cache.get(cache_key_hash)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key_hash, result, ttl)

            return result

        return wrapper

    return decorator


class QueryCache:
    """
    Specialized cache for database queries.

    Usage:
        query_cache = QueryCache()

        # Check cache first
        result = query_cache.get("user_sessions_123")
        if result is None:
            result = db.query(...).all()
            query_cache.set("user_sessions_123", result)
    """

    def __init__(self):
        self.cache = get_cache_manager()

    def build_key(self, *args) -> str:
        """Build cache key from arguments"""
        key_str = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        return self.cache.get_cached_query(key)

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set in cache"""
        self.cache.cache_query_result(key, value, ttl)

    def invalidate(self, pattern: Optional[str] = None):
        """Invalidate cache entries matching pattern"""
        if pattern:
            # For Redis with pattern support
            if self.cache.redis_client:
                try:
                    keys = self.cache.redis_client.keys(f"query:{pattern}*")
                    if keys:
                        self.cache.redis_client.delete(*keys)
                except Exception as e:
                    print(f"Cache invalidation error: {e}")
        else:
            # Clear all query cache
            self.cache.clear()
