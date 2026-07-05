import os
import redis
from src.utils.logger import get_logger

logger = get_logger("redis_client")

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_timeout=5.0
    )
    logger.info(f"Redis client initialized targeting: redis://{REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.error(f"Failed to initialize Redis client: {e}")
    redis_client = None
