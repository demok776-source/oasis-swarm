"""
Shared security primitives for app-tier: rate limiting + optional API-key auth.

Before this module existed, every route (including /ai/query, which drives
a local Ollama LLM call, and /sync/publish, which fans out to every
connected WebSocket client) had zero protection -- no auth, no rate limit.
Anyone with the URL could burn compute or spam the event bus for free.

Two independent layers:

1. Rate limiting (slowapi, backed by Redis when available so limits are
   shared across multiple Cloud Run instances -- an in-memory limiter would
   let each instance's traffic bypass the others' counters). Falls back to
   in-memory automatically if Redis is unreachable, so this never becomes a
   hard dependency for local dev.

2. API key auth (`require_api_key` dependency), gated by the `APP_API_KEY`
   env var. If that var is unset, auth is a no-op with a one-time startup
   warning -- this keeps `docker-compose up` working out of the box for
   local dev without forcing a key on every contributor's laptop. Set
   APP_API_KEY (via Secret Manager in prod, see infra/deploy.sh step 3)
   to actually enforce it.
"""
import os

from fastapi import Header, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.utils.logger import get_logger

logger = get_logger("security")

APP_API_KEY = os.environ.get("APP_API_KEY")
if not APP_API_KEY:
    logger.warning(
        "APP_API_KEY is not set -- API key auth is DISABLED. Every route protected by "
        "require_api_key() is open to anyone who can reach this service. Set APP_API_KEY "
        "(Secret Manager in prod) to enable it."
    )


def _redis_storage_uri() -> str:
    host = os.environ.get("REDIS_HOST", "127.0.0.1")
    port = os.environ.get("REDIS_PORT", "6379")
    db = os.environ.get("REDIS_DB", "0")
    password = os.environ.get("REDIS_PASSWORD")
    auth = f":{password}@" if password else ""
    return f"redis://{auth}{host}:{port}/{db}"


def _build_limiter() -> Limiter:
    """Use Redis-backed rate-limit storage when Redis is actually reachable
    (required for limits to be shared across multiple Cloud Run instances);
    otherwise fall back to slowapi's in-memory storage.

    Constructing Limiter(storage_uri="redis://...") does NOT fail eagerly if
    Redis is down -- the connection is only attempted lazily on the first
    rate-limit check, which would turn every single request into a 500
    instead of gracefully degrading. So we probe Redis ourselves first.
    """
    import redis as redis_lib

    host = os.environ.get("REDIS_HOST", "127.0.0.1")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    db = int(os.environ.get("REDIS_DB", "0"))
    password = os.environ.get("REDIS_PASSWORD")

    try:
        probe = redis_lib.Redis(host=host, port=port, db=db, password=password, socket_timeout=1.0)
        probe.ping()
        return Limiter(key_func=get_remote_address, storage_uri=_redis_storage_uri())
    except Exception as e:
        logger.warning(
            f"Redis unreachable ({e}) -- rate limiter falling back to in-memory storage. "
            f"Fine for local dev; on Cloud Run with multiple instances this means each "
            f"instance enforces its own separate limit until Redis is reachable."
        )
        return Limiter(key_func=get_remote_address)


limiter = _build_limiter()


async def require_api_key(x_api_key: str = Header(default=None)) -> None:
    """FastAPI dependency: enforces the X-API-Key header when APP_API_KEY is
    configured. No-ops (with the startup warning above) when it isn't."""
    if not APP_API_KEY:
        return
    if x_api_key != APP_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing X-API-Key header")
