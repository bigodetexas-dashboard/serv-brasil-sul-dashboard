"""
Simple In-Memory Cache

Provides a thread-safe LRU cache for frequently accessed data
to reduce database queries and improve performance.
"""

import time
import threading
from typing import Any, Optional, Callable
from functools import wraps
from collections import OrderedDict


class LRUCache:
    """
    Thread-safe Least Recently Used (LRU) cache.

    Stores frequently accessed data in memory with automatic expiration
    and size limits to prevent memory bloat.
    """

    def __init__(self, max_size: int = 1000, ttl: int = 300) -> None:
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of items in cache
            ttl: Time-to-live in seconds (default 5 minutes)
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, timestamp = self._cache[key]

            # Check if expired
            if time.time() - timestamp > self.ttl:
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return value

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            # Remove oldest if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._cache.popitem(last=False)

            self._cache[key] = (value, time.time())
            self._cache.move_to_end(key)

    def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hits, misses, size, and hit rate
        """
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "size": len(self._cache),
                "hit_rate": round(hit_rate, 2),
            }


# Global cache instance
_cache: Optional[LRUCache] = None
_cache_lock = threading.Lock()


def get_cache() -> LRUCache:
    """Get or create the global cache instance."""
    global _cache

    if _cache is None:
        with _cache_lock:
            if _cache is None:
                _cache = LRUCache()

    return _cache


def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        key_func: Optional function to generate cache key from args

    Example:
        >>> @cached(ttl=60)
        ... def get_user(user_id):
        ...     return db.query(user_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cache = get_cache()
            result = cache.get(cache_key)

            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)

            return result

        return wrapper

    return decorator
