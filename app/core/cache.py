"""
Caching layer with Redis integration and cache invalidation strategies.
"""

import json
import asyncio
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from functools import wraps
import redis.asyncio as redis
from app.core.config import get_settings
from app.utils.logger import get_logger


class CacheBackend(ABC):
    """Abstract cache backend interface."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache."""
        pass


class RedisCache(CacheBackend):
    """Redis cache backend."""
    
    def __init__(self, redis_url: str, db: int = 0):
        self.redis_url = redis_url
        self.db = db
        self._redis: Optional[redis.Redis] = None
        self.logger = get_logger("redis_cache", structured=True)
    
    async def _get_redis(self) -> redis.Redis:
        """Get Redis connection."""
        if self._redis is None or not self._redis.ping():
            try:
                self._redis = await redis.from_url(
                    self.redis_url,
                    db=self.db,
                    decode_responses=True
                )
                await self._redis.ping()
                self.logger.info("Redis connection established")
            except Exception as e:
                self.logger.error(f"Failed to connect to Redis: {e}")
                raise
        return self._redis
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            redis_client = await self._get_redis()
            value = await redis_client.get(key)
            if value is None:
                return None
            
            # Deserialize JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            self.logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        try:
            redis_client = await self._get_redis()
            
            # Serialize to JSON
            try:
                serialized_value = json.dumps(value, default=str)
            except (TypeError, ValueError):
                serialized_value = str(value)
            
            # Set with TTL if provided
            if ttl:
                success = await redis_client.setex(key, ttl, serialized_value)
            else:
                success = await redis_client.set(key, serialized_value)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.exists(key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all Redis cache."""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.flushdb()
            return result
            
        except Exception as e:
            self.logger.error(f"Cache clear error: {e}")
            return False


class MemoryCache(CacheBackend):
    """In-memory cache backend for development and testing."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger("memory_cache", structured=True)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        try:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry["expires_at"] and datetime.utcnow() > entry["expires_at"]:
                del self._cache[key]
                return None
            
            return entry["value"]
            
        except Exception as e:
            self.logger.error(f"Memory cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache."""
        try:
            expires_at = None
            if ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at
            }
            return True
            
        except Exception as e:
            self.logger.error(f"Memory cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache."""
        try:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Memory cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        try:
            return key in self._cache and await self.get(key) is not None
            
        except Exception as e:
            self.logger.error(f"Memory cache exists error for key {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all memory cache."""
        try:
            self._cache.clear()
            return True
            
        except Exception as e:
            self.logger.error(f"Memory cache clear error: {e}")
            return False


class CacheManager:
    """Cache manager with invalidation strategies."""
    
    def __init__(self, backend: CacheBackend):
        self.backend = backend
        self.logger = get_logger("cache_manager", structured=True)
        self._invalidators: Dict[str, List[Callable]] = {}
    
    def register_invalidator(self, pattern: str, invalidator: Callable):
        """Register a cache invalidator for a specific pattern."""
        if pattern not in self._invalidators:
            self._invalidators[pattern] = []
        self._invalidators[pattern].append(invalidator)
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern."""
        try:
            for invalidator in self._invalidators.get(pattern, []):
                await invalidator()
            
            self.logger.info(f"Cache invalidation triggered for pattern: {pattern}")
            
        except Exception as e:
            self.logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            # This is backend-specific, implement as needed
            return {
                "backend_type": self.backend.__class__.__name__,
                "invalidators_registered": len(self._invalidators)
            }
        except Exception as e:
            self.logger.error(f"Cache stats error: {e}")
            return {}


def cache_key_generator(prefix: str, **kwargs) -> str:
    """Generate cache key from parameters."""
    # Create a sorted representation of kwargs
    sorted_items = sorted(kwargs.items())
    key_parts = [prefix]
    
    for key, value in sorted_items:
        key_parts.append(f"{key}:{value}")
    
    return ":".join(key_parts)


def cached_result(
    cache_manager: CacheManager,
    prefix: str,
    ttl: Optional[int] = 300,  # 5 minutes default
    key_generator: Optional[Callable] = None
):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                cache_key = key_generator(prefix=prefix, **kwargs)
            else:
                cache_key = cache_key_generator(prefix, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_manager.backend.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.backend.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache instances
_cache_backend: Optional[CacheBackend] = None
_cache_manager: Optional[CacheManager] = None


def initialize_cache(backend: Optional[CacheBackend] = None) -> CacheManager:
    """Initialize the global cache system."""
    global _cache_backend, _cache_manager
    
    if backend is None:
        settings = get_settings()
        
        # Try Redis first, fallback to memory cache
        try:
            redis_url = f"redis://localhost:6379/0"
            _cache_backend = RedisCache(redis_url)
        except Exception as e:
            get_logger("cache_init", structured=True).warning(f"Redis unavailable, using memory cache: {e}")
            _cache_backend = MemoryCache()
    else:
        _cache_backend = backend
    
    _cache_manager = CacheManager(_cache_backend)
    
    # Set up cache invalidators
    _setup_cache_invalidators()
    
    return _cache_manager


def get_cache_manager() -> CacheManager:
    """Get the global cache manager."""
    if _cache_manager is None:
        raise RuntimeError("Cache system not initialized. Call initialize_cache() first.")
    return _cache_manager


def _setup_cache_invalidators():
    """Set up cache invalidators."""
    cache_manager = get_cache_manager()
    
    # User cache invalidators
    async def invalidate_user_cache():
        # Invalidate user-related caches
        pass
    
    # Post cache invalidators  
    async def invalidate_post_cache():
        # Invalidate post-related caches
        pass
    
    # Register invalidators
    cache_manager.register_invalidator("user:*", invalidate_user_cache)
    cache_manager.register_invalidator("post:*", invalidate_post_cache)