import redis  
import redis.asyncio as async_redis 
from core.config import settings

# 1. Client dùng cho FastAPI (Async) - Để lắng nghe Pub/Sub mà không treo server
async_redis_client = async_redis.from_url(
    settings.redis_url, 
    decode_responses=True
)

# 2. Client dùng cho Celery Worker (Sync) - Để publish kết quả ngay lập tức
sync_redis_client = redis.from_url(
    settings.redis_url, 
    decode_responses=True
)