from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import json
from src.db import get_db
from src.redis import redis_client
from src.crud import create_sync_event
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
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send broadcast: {e}")

manager = ConnectionManager()

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

def is_redis_available() -> bool:
    global redis_client
    if redis_client is None:
        return False
    try:
        redis_client.ping()
        return True
    except Exception:
        return False

@router.post("/publish")
async def publish_sync_event(message: SyncMessage, db: Session = Depends(get_db)):
    logger.info(f"Sync event received from module '{message.module}': {message.event}")
    
    if not is_redis_available():
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
            redis_client.publish(channel, f"{message.event}::{str(message.payload)}")
            
        # Broadcast the online event
        await manager.broadcast({
            "source": "Redis-PubSub",
            "module": message.module,
            "event": message.event,
            "payload": message.payload
        })
        return {
            "status": "success",
            "channel": channel,
            "event": message.event
        }
    except Exception as e:
        logger.error(f"Redis publication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"// SYNC ERROR: {str(e)}"
        )
