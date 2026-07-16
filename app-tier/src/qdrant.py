import os
from qdrant_client import QdrantClient, AsyncQdrantClient
from src.utils.logger import get_logger

logger = get_logger("qdrant_client")

QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
QDRANT_KEY = os.getenv("QDRANT_KEY", None)

try:
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_KEY,
        timeout=5.0
    )
    logger.info(f"Qdrant client initialized targeting: {QDRANT_URL}")
except Exception as e:
    logger.error(f"Failed to initialize Qdrant client: {e}")
    qdrant_client = None

# Async counterpart, used by is_qdrant_available() -- see src/redis.py's
# async_redis_client for the full rationale (blocking sync client calls
# inside `async def` handlers freeze the whole event loop, not just the
# current request, whenever the backing service is slow or unreachable).
try:
    async_qdrant_client = AsyncQdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_KEY,
        timeout=5.0
    )
except Exception as e:
    logger.error(f"Failed to initialize async Qdrant client: {e}")
    async_qdrant_client = None

async def is_qdrant_available():
    if async_qdrant_client is None:
        return False
    try:
        # Check if we can get collections, which verifies the connection
        await async_qdrant_client.get_collections()
        return True
    except Exception:
        return False
