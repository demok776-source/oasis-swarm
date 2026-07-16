from fastapi import APIRouter, HTTPException, status, Depends, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import json
import os
import asyncio
from src.db import get_db
from src.redis import redis_client, async_redis_client
from src.crud import create_sync_event
from src.security import limiter, require_api_key
from src.utils.logger import get_logger
import threading
from kafka import KafkaProducer

logger = get_logger("sync_route")

# Initialize Kafka Producer (Fire and Forget for high throughput)
try:
    kafka_producer = KafkaProducer(
        bootstrap_servers=['kafka:29092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
except Exception as e:
    logger.error(f"Kafka Producer failed to initialize: {e}")
    kafka_producer = None

router = APIRouter(prefix="/sync", tags=["Sync Layer"])

class SyncMessage(BaseModel):
    module: str
    event: str
    payload: dict

WS_BROADCAST_CHANNEL = "oasis:ws:broadcast"

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection accepted. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Remaining active: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Publishes to Redis so every gunicorn worker / Cloud Run instance
        relays the message to its own locally-connected clients (see
        redis_ws_relay_loop below). Falls back to local-only delivery if
        Redis is unreachable -- correct for single-worker dev, incomplete
        for multi-worker/multi-instance deployments (which is exactly the
        gap this whole mechanism exists to close)."""
        try:
            await async_redis_client.publish(WS_BROADCAST_CHANNEL, json.dumps(message))
            return
        except Exception as e:
            logger.error(f"Redis publish for WS broadcast failed, falling back to local-only send: {e}")
        await self.send_local(message)

    async def send_local(self, message: dict):
        # Snapshot before iterating: a concurrent disconnect() mutating
        # active_connections mid-broadcast could otherwise skip a client.
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send broadcast: {e}")

manager = ConnectionManager()


async def redis_ws_relay_loop():
    """Background task (started from main.py's lifespan): subscribes to the
    cross-worker broadcast channel and relays every message to THIS
    worker's local WebSocket connections. Without this, ConnectionManager
    on a multi-worker/multi-instance deployment is broadcast-blind outside
    its own process.

    Uses redis.asyncio (not the sync `redis` client + run_in_executor
    polling) so it integrates natively with whatever event loop is
    running -- including TestClient's anyio-portal loop in tests, where a
    thread-offloaded blocking poll turned out to never get scheduled and
    silently hung any test that published a broadcast and waited to
    receive it back on the same connection.
    """
    import redis.asyncio as aioredis

    if redis_client is None:
        logger.warning("Redis unavailable at startup — WS broadcasts will be local-to-this-process only.")
        return

    host = os.environ.get("REDIS_HOST", "127.0.0.1")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    db = int(os.environ.get("REDIS_DB", "0"))
    password = os.environ.get("REDIS_PASSWORD")

    try:
        aio_client = aioredis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
        pubsub = aio_client.pubsub()
        await pubsub.subscribe(WS_BROADCAST_CHANNEL)
    except Exception as e:
        logger.error(f"Failed to subscribe to {WS_BROADCAST_CHANNEL}: {e}")
        return

    logger.info(f"Subscribed to Redis channel '{WS_BROADCAST_CHANNEL}' for cross-worker WS relay.")
    try:
        async for msg in pubsub.listen():
            if msg.get("type") != "message":
                continue
            try:
                data = json.loads(msg["data"])
                await manager.send_local(data)
            except Exception as e:
                logger.error(f"Error relaying WS broadcast: {e}")
    except asyncio.CancelledError:
        await pubsub.close()
        await aio_client.close()
        raise

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open and await frames
            data = await websocket.receive_text()
            logger.info(f"WebSocket data received: {data}")
            try:
                msg = json.loads(data)
                await manager.broadcast(msg)
            except Exception:
                await manager.broadcast({"source": "WS-Client", "message": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket exception: {e}")
        manager.disconnect(websocket)

async def is_redis_available() -> bool:
    if async_redis_client is None:
        return False
    try:
        await async_redis_client.ping()
        return True
    except Exception:
        return False

@router.post("/publish", dependencies=[Depends(require_api_key)])
@limiter.limit("60/minute")
async def publish_sync_event(request: Request, message: SyncMessage, db: Session = Depends(get_db)):
    logger.info(f"Sync event received from module '{message.module}': {message.event}")
    
    if not await is_redis_available():
        logger.warning("Redis client offline. Recording event to database sync queue.")
        try:
            db_event = create_sync_event(db, message.module, message.event, message.payload)
            # Broadcast the offline event
            await manager.broadcast({
                "source": "DB-Fallback",
                "module": message.module,
                "event": message.event,
                "payload": message.payload
            })
            return {
                "status": "dry_run",
                "module": message.module,
                "event": message.event,
                "db_event_id": db_event.id,
                "info": "// Redis connection offline - saved to DB queue"
            }
        except Exception as e:
            logger.error(f"DB event logging failed: {e}")
            return {
                "status": "dry_run",
                "module": message.module,
                "event": message.event,
                "info": f"// Redis offline - DB log failed: {str(e)}"
            }
    
    try:
        # Publish to unified Redis pub/sub channel
        channel = f"oasis:channel:{message.module}"
        
        if message.event == "DRONE_TELEMETRY_UPDATE" and kafka_producer:
            # Publish to Kafka for high-velocity aerospace telemetry
            kafka_producer.send("telemetry.aerospace", value={"module": message.module, "payload": message.payload})
            logger.info("Published aerospace telemetry directly to Kafka stream.")
        else:
            # Standard Redis flow
            await async_redis_client.publish(channel, f"{message.event}::{str(message.payload)}")
            
        # Broadcast the online event
        await manager.broadcast({
            "source": "Redis-PubSub",
            "module": message.module,
            "event": message.event,
            "payload": message.payload
        })
        return {
            "status": "success",
            "module": message.module,
            "channel": channel,
            "event": message.event
        }
    except Exception as e:
        logger.error(f"Redis publication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"// SYNC ERROR: {str(e)}"
        )
