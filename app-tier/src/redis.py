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

# Async counterpart for use inside `async def` route handlers / background
# asyncio tasks. `redis_client` above is the synchronous redis-py client --
# calling its blocking methods (e.g. .publish()) directly from async code
# stalls the whole event loop for up to socket_timeout seconds on every
# call, not just the current request. Use this client from async contexts
# instead; keep the sync one for genuinely synchronous code paths (e.g. the
# background-thread DB-polling fallback in main.py, which isn't on the
# event loop at all).
import redis.asyncio as _redis_asyncio

async_redis_client = _redis_asyncio.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_timeout=5.0,
)
