import redis.asyncio as redis
from infrastructure.config import get_settings
import structlog
import json
from typing import Any, Optional

logger = structlog.get_logger()
settings = get_settings()

class RedisClient:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None):
        """Set a key-value pair"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.set(key, value, ex=expire)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def delete(self, key: str):
        """Delete a key"""
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.redis.exists(key)
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

# Global Redis client instance
redis_client = RedisClient()

async def get_redis():
    if not redis_client.redis:
        await redis_client.connect()
    return redis_client
