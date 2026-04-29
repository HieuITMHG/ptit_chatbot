import redis  
import redis.asyncio as async_redis 
from core.config import settings

async_redis_client = async_redis.from_url(
    settings.redis_url, 
    decode_responses=True
)

sync_redis_client = redis.from_url(
    settings.redis_url, 
    decode_responses=True
)