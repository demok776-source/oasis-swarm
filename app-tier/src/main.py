import os
import time
import asyncio
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.routes import health, contact, ai, sync
from src.security import limiter
from src.utils.logger import get_logger

logger = get_logger("app_main")

# ---------------------------------------------------------------------------
# Alembic migrations — run once at import time, before the app object exists.
# ---------------------------------------------------------------------------
from alembic.config import Config
from alembic import command

try:
    logger.info("Running Alembic migrations on startup...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ini_path = os.path.join(base_dir, "alembic.ini")
    alembic_cfg = Config(ini_path)
    command.upgrade(alembic_cfg, "head")
    logger.info("Alembic migrations completed successfully.")
except Exception as e:
    logger.error(f"Failed to auto-run migrations on startup: {e}")

# ---------------------------------------------------------------------------
# Background Sync Layer listener (Redis Pub/Sub with DB-polling fallback)
# ---------------------------------------------------------------------------
sync_listener_active = False
pubsub_thread = None
main_event_loop: asyncio.AbstractEventLoop | None = None
_sync_listener_thread: threading.Thread | None = None
_relay_task: asyncio.Task | None = None


def handle_redis_message(message):
    try:
        channel = message.get("channel", "")
        data = message.get("data", "")
        logger.info(f"// SYNC LAYER EVENT — Channel: {channel} | Payload: {data}")

        is_critical = (b"CRITICAL_FAILURE" in data) if isinstance(data, bytes) else ("CRITICAL_FAILURE" in str(data))
        if is_critical:
            logger.warning("JARVIS INTERVENTION: Critical failure detected. Invoking agent self-healing...")
            try:
                from src.routes.ai import trigger_self_healing
                res = trigger_self_healing(component="System")
                logger.info(f"JARVIS Response: {res}")
            except Exception as e:
                logger.error(f"JARVIS failed to heal: {e}")
    except Exception as ex:
        logger.error(f"Error handling pub/sub message: {ex}")


def _broadcast_from_thread(payload: dict):
    """Safely hand a broadcast off to the main asyncio event loop.

    `sync_listener_loop` runs in a plain OS thread, not on the loop that
    owns the live WebSocket connections in `ConnectionManager`. Calling
    `asyncio.run(manager.broadcast(...))` here would spin up a *second*,
    unrelated event loop in this thread and hand it ASGI WebSocket objects
    that belong to the server's loop — which is undefined behavior at best
    (silently dropped sends) and a hard crash at worst
    ("Task attached to a different loop").

    `run_coroutine_threadsafe` is the documented, correct way to submit a
    coroutine to a loop running in a different thread.
    """
    from src.routes.sync import manager

    if main_event_loop is None:
        logger.error("Cannot broadcast: main event loop not captured yet.")
        return
    try:
        future = asyncio.run_coroutine_threadsafe(manager.broadcast(payload), main_event_loop)
        future.result(timeout=5)
    except Exception as ex:
        logger.error(f"WebSocket broadcast error from background thread: {ex}")


def sync_listener_loop():
    global sync_listener_active, pubsub_thread
    logger.info("Background Sync Layer listener loop started.")

    from src.redis import redis_client
    from src.db import SessionLocal
    from src.models import SyncEventHistory

    redis_online = False
    last_processed_id = 0

    db = SessionLocal()
    try:
        max_id_row = db.query(SyncEventHistory).order_by(SyncEventHistory.id.desc()).first()
        if max_id_row:
            last_processed_id = max_id_row.id
            logger.info(f"Initial DB Sync Event offset set to ID: {last_processed_id}")
    except Exception as e:
        logger.info(f"No previous events found or DB not initialized: {e}")
    finally:
        db.close()

    while sync_listener_active:
        try:
            if redis_client is not None:
                redis_client.ping()
                if not redis_online:
                    logger.info("Redis detected online. Switching listener to Redis Pub/Sub mode.")
                    redis_online = True
                    pubsub = redis_client.pubsub()
                    pubsub.psubscribe(**{"oasis:channel:*": handle_redis_message})
                    pubsub_thread = pubsub.run_in_thread(sleep_time=0.1, daemon=True)
            else:
                redis_online = False
        except Exception:
            if redis_online:
                logger.warning("Redis connection lost. Falling back to DB Polling mode.")
                redis_online = False
                if pubsub_thread is not None:
                    try:
                        pubsub_thread.stop()
                    except Exception:
                        pass
                    pubsub_thread = None

        if not redis_online:
            db = SessionLocal()
            try:
                new_events = (
                    db.query(SyncEventHistory)
                    .filter(SyncEventHistory.id > last_processed_id)
                    .order_by(SyncEventHistory.id.asc())
                    .all()
                )
                if new_events:
                    import ast

                    for ev in new_events:
                        logger.info(
                            f"// SYNC LAYER EVENT (DB-Fallback) — Channel: oasis:channel:{ev.module} | "
                            f"Payload: {ev.event}::{ev.payload}"
                        )
                        last_processed_id = ev.id
                        try:
                            payload_dict = ast.literal_eval(ev.payload) if isinstance(ev.payload, str) else ev.payload
                        except Exception:
                            payload_dict = {"raw": ev.payload}
                        _broadcast_from_thread({
                            "source": "DB-Fallback-Listener",
                            "module": ev.module,
                            "event": ev.event,
                            "payload": payload_dict,
                        })
            except Exception:
                pass
            finally:
                db.close()

        time.sleep(1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    global sync_listener_active, main_event_loop, _sync_listener_thread, _relay_task
    main_event_loop = asyncio.get_running_loop()
    sync_listener_active = True

    if _sync_listener_thread is None or not _sync_listener_thread.is_alive():
        _sync_listener_thread = threading.Thread(target=sync_listener_loop, daemon=True)
        _sync_listener_thread.start()
        logger.info("Sync Layer listener thread started; main event loop captured for cross-thread broadcast.")
    else:
        logger.info("Sync Layer listener thread already running; reusing it (re-entered lifespan).")

    if _relay_task is None or _relay_task.done():
        from src.routes.sync import redis_ws_relay_loop
        _relay_task = asyncio.create_task(redis_ws_relay_loop())
    else:
        logger.info("Redis WS relay task already running; reusing it (re-entered lifespan).")

    yield

    # --- shutdown ---
    logger.info("Stopping background Sync Layer listener...")
    sync_listener_active = False
    if pubsub_thread is not None:
        try:
            pubsub_thread.stop()
        except Exception:
            pass


_is_production = os.environ.get("ENVIRONMENT", "development").lower() == "production"

app = FastAPI(
    title="OASIS SYSTEM CORE — app-tier Service",
    description="Central back-end processing core for the 13-module autonomous organism.",
    version="1.0.0",
    lifespan=lifespan,
    # Previously always exposed regardless of environment -- anyone could
    # browse the full OpenAPI schema (every route, every field) at /docs.
    # Set ENVIRONMENT=production to disable; defaults to enabled for local dev.
    docs_url=None if _is_production else "/docs",
    redoc_url=None if _is_production else "/redoc",
    openapi_url=None if _is_production else "/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS. `allow_origins=["*"]` combined with `allow_credentials=True` is
# rejected by browsers per the Fetch spec (a wildcard origin cannot carry
# credentials) — Starlette will echo `*` back and the browser will simply
# refuse to expose the response to JS. Use an explicit, env-configurable
# allow-list instead so credentialed requests actually work.
# ---------------------------------------------------------------------------
_default_origins = "http://localhost:3000,http://127.0.0.1:3000,https://oasis-system-core.com,https://www.oasis-system-core.com"
CORS_ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ALLOWED_ORIGINS", _default_origins).split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(health.router)
app.include_router(contact.router)
app.include_router(ai.router)
app.include_router(sync.router)


@app.get("/")
async def root_index():
    return {
        "message": "JARVIS v40.0 online.",
        "layer": "Autonomous Omni-Eternity Layer active. Central intelligence of OASIS SYSTEM CORE - 13 modules, one organism.",
    }


@app.get("/health/telemetry")
async def get_telemetry():
    import psutil

    from src.db import SessionLocal
    from src.models import Contact, SyncEventHistory
    from src.routes.sync import manager, is_redis_available
    from src.qdrant import is_qdrant_available

    db_size_bytes = 0
    if os.path.exists("oasis.db"):
        try:
            db_size_bytes = os.path.getsize("oasis.db")
        except Exception:
            pass

    ws_count = len(manager.active_connections)

    contacts_count = 0
    events_count = 0
    db = SessionLocal()
    try:
        contacts_count = db.query(Contact).count()
        events_count = db.query(SyncEventHistory).count()
    except Exception:
        pass
    finally:
        db.close()

    redis_status = "ONLINE" if await is_redis_available() else "FALLBACK"
    qdrant_status = "ONLINE" if await is_qdrant_available() else "FALLBACK"

    # Real process/host metrics (psutil) — no more sine-wave placeholder data.
    cpu_usage = psutil.cpu_percent(interval=0.05)
    ram_usage = psutil.virtual_memory().percent

    return {
        "status": "ONLINE",
        "cpu_usage": round(cpu_usage, 2),
        "ram_usage": round(ram_usage, 2),
        "db_size_kb": round(db_size_bytes / 1024, 2),
        "ws_connections": ws_count,
        "contacts_count": contacts_count,
        "events_count": events_count,
        "redis_status": redis_status,
        "qdrant_status": qdrant_status,
    }
