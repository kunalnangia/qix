import redis
from app.core.config import settings

def get_redis_client():
    """
    Initializes and returns a Redis client.
    """
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True  # Decode responses to strings
    )

# Global Redis client instance
redis_client = get_redis_client()
