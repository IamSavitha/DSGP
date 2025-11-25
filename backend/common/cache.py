"""
Redis caching utilities for the Kayak Simulation system.
"""
import redis
import json
from typing import Optional, Any, Union
from functools import wraps
import hashlib
import logging

from .config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager with connection pooling."""
    
    _instance: Optional['RedisCache'] = None
    _pool: Optional[redis.ConnectionPool] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                max_connections=50,
                decode_responses=True
            )
        return cls._instance
    
    @property
    def client(self) -> redis.Redis:
        """Get Redis client from connection pool."""
        return redis.Redis(connection_pool=self._pool)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value, default=str)
            return self.client.setex(key, ttl, serialized)
        except (redis.RedisError, TypeError) as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.client.exists(key))
        except redis.RedisError as e:
            logger.warning(f"Cache exists error for key {key}: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache."""
        try:
            return self.client.incrby(key, amount)
        except redis.RedisError as e:
            logger.warning(f"Cache increment error for key {key}: {e}")
            return None
    
    def get_hash(self, key: str, field: str = None) -> Optional[Any]:
        """Get hash value(s) from cache."""
        try:
            if field:
                value = self.client.hget(key, field)
                return json.loads(value) if value else None
            else:
                values = self.client.hgetall(key)
                return {k: json.loads(v) for k, v in values.items()} if values else None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Cache hash get error for key {key}: {e}")
            return None
    
    def set_hash(self, key: str, field: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set hash value in cache."""
        try:
            serialized = json.dumps(value, default=str)
            result = self.client.hset(key, field, serialized)
            if ttl:
                self.client.expire(key, ttl)
            return bool(result)
        except (redis.RedisError, TypeError) as e:
            logger.warning(f"Cache hash set error for key {key}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache (use with caution)."""
        try:
            return self.client.flushdb()
        except redis.RedisError as e:
            logger.error(f"Cache clear error: {e}")
            return False


# ==================== Cache Key Generators ====================

class CacheKeys:
    """Cache key generators for different entities."""
    
    PREFIX = "kayak"
    
    @staticmethod
    def user(user_id: str) -> str:
        return f"{CacheKeys.PREFIX}:user:{user_id}"
    
    @staticmethod
    def user_bookings(user_id: str) -> str:
        return f"{CacheKeys.PREFIX}:user:{user_id}:bookings"
    
    @staticmethod
    def flight(flight_id: str) -> str:
        return f"{CacheKeys.PREFIX}:flight:{flight_id}"
    
    @staticmethod
    def flight_search(params_hash: str) -> str:
        return f"{CacheKeys.PREFIX}:flight_search:{params_hash}"
    
    @staticmethod
    def hotel(hotel_id: str) -> str:
        return f"{CacheKeys.PREFIX}:hotel:{hotel_id}"
    
    @staticmethod
    def hotel_search(params_hash: str) -> str:
        return f"{CacheKeys.PREFIX}:hotel_search:{params_hash}"
    
    @staticmethod
    def car(car_id: str) -> str:
        return f"{CacheKeys.PREFIX}:car:{car_id}"
    
    @staticmethod
    def car_search(params_hash: str) -> str:
        return f"{CacheKeys.PREFIX}:car_search:{params_hash}"
    
    @staticmethod
    def billing(billing_id: str) -> str:
        return f"{CacheKeys.PREFIX}:billing:{billing_id}"
    
    @staticmethod
    def admin_analytics(report_type: str) -> str:
        return f"{CacheKeys.PREFIX}:admin:analytics:{report_type}"
    
    @staticmethod
    def listing_reviews(listing_type: str, listing_id: str) -> str:
        return f"{CacheKeys.PREFIX}:reviews:{listing_type}:{listing_id}"


def generate_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


# ==================== Cache Decorators ====================

def cached(
    key_prefix: str,
    ttl: int = None,
    key_builder: callable = None
):
    """
    Decorator for caching function results.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
        key_builder: Optional function to build cache key from args
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = RedisCache()
            
            # Build cache key
            if key_builder:
                cache_key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
            else:
                cache_key = f"{key_prefix}:{generate_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl)
                logger.debug(f"Cached result for key: {cache_key}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = RedisCache()
            
            # Build cache key
            if key_builder:
                cache_key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
            else:
                cache_key = f"{key_prefix}:{generate_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl)
                logger.debug(f"Cached result for key: {cache_key}")
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def invalidate_cache(key_pattern: str):
    """
    Decorator to invalidate cache after function execution.
    
    Args:
        key_pattern: Pattern for cache keys to invalidate
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            cache = RedisCache()
            cache.delete_pattern(key_pattern)
            logger.debug(f"Invalidated cache for pattern: {key_pattern}")
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache = RedisCache()
            cache.delete_pattern(key_pattern)
            logger.debug(f"Invalidated cache for pattern: {key_pattern}")
            return result
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator

