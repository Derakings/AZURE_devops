"""
Redis caching utilities
"""

import json
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings

# Redis client instance
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    client = await get_redis()
    value = await client.get(key)
    if value:
        return json.loads(value)
    return None


async def cache_set(key: str, value: Any, ttl: int = None) -> bool:
    """Set value in cache with TTL"""
    client = await get_redis()
    ttl = ttl or settings.REDIS_CACHE_TTL
    serialized = json.dumps(value)
    return await client.setex(key, ttl, serialized)


async def cache_delete(key: str) -> bool:
    """Delete key from cache"""
    client = await get_redis()
    return await client.delete(key) > 0


async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching pattern"""
    client = await get_redis()
    keys = await client.keys(pattern)
    if keys:
        return await client.delete(*keys)
    return 0


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
