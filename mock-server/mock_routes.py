from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import re
import os
import redis
import httpx

router = APIRouter(tags=["Mock Services"])

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
APP_TIER_URL = os.getenv("APP_TIER_URL", "http://127.0.0.1:8080")

# Redis client configuration for mock emit
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
try:
    mock_redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_timeout=2.0)
except Exception:
    mock_redis = None

class ContactRequest(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Dima Dynamo"})
    email: str = Field(..., json_schema_extra={"example": "oasis@core.dev"})
    message: str = Field(..., json_schema_extra={"example": "Testing local mock transmission."})

class QueryRequest(BaseModel):
    query: str
    collection: str = "oasis_docs"

class SyncMessage(BaseModel):
    module: str
    event: str
    payload: dict

class EmitEventRequest(BaseModel):
    module: str
    event: str
    payload: dict = {}

@router.post("/contact", status_code=status.HTTP_201_CREATED)
async def mock_submit_contact(payload: ContactRequest):
    print(f"[MOCK-DB] Saving contact submission from: {payload.email}")
    
    # Input validations
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="// VALIDATION ERROR: Name cannot be empty.")
    if not re.match(EMAIL_REGEX, payload.email):
        raise HTTPException(status_code=400, detail="// VALIDATION ERROR: Invalid email address format.")
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="// VALIDATION ERROR: Message cannot be empty.")
        
    print(f"[MOCK-DB] Saved! Data: name='{payload.name}', email='{payload.email}', message_len={len(payload.message)}")
    return {
        "status": "ok",
        "id": 999, 
        "info": "// MOCK SUCCESS: Written to mock transient data storage."
    }

@router.post("/ai/query")
async def mock_query_jarvis_memory(payload: QueryRequest):
    print(f"[MOCK-AI] Querying mock memory in collection '{payload.collection}': {payload.query}")
    return {
        "status": "mocked",
        "collection": payload.collection,
        "query": payload.query,
        "results": [
            {"id": 1, "score": 0.95, "payload": {"text": "Autonomous Omni-Eternity Layer activated."}},
            {"id": 2, "score": 0.88, "payload": {"text": "Central intelligence of OASIS SYSTEM CORE - 13 modules."}}
        ]
    }

@router.post("/sync/publish")
async def mock_publish_sync_event(message: SyncMessage):
    print(f"[MOCK-SYNC] Sync event from '{message.module}': {message.event}")
    return {
        "status": "success",
        "channel": f"oasis:channel:{message.module}",
        "event": message.event,
        "info": "// MOCK SUCCESS: Published to local transient event bus."
    }

@router.post("/emit")
async def mock_emit_event(payload: EmitEventRequest):
    print(f"[MOCK-SYNC] Emitting test event from module '{payload.module}': {payload.event}")
    
    redis_online = False
    if mock_redis is not None:
        try:
            mock_redis.ping()
            redis_online = True
        except Exception:
            redis_online = False
            
    if redis_online:
        try:
            channel = f"oasis:channel:{payload.module}"
            mock_redis.publish(channel, f"{payload.event}::{str(payload.payload)}")
            return {
                "status": "success",
                "channel": channel,
                "event": payload.event
            }
        except Exception:
            pass

    # Redis offline -> Forward to App-Tier Backend
    print(f"[MOCK-SYNC] Local Redis offline. Forwarding event to App-Tier at {APP_TIER_URL}...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{APP_TIER_URL}/sync/publish",
                json={
                    "module": payload.module,
                    "event": payload.event,
                    "payload": payload.payload
                },
                timeout=2.0
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "channel": f"oasis:channel:{payload.module}",
                    "event": payload.event,
                    "info": f"// Redis offline - forwarded to App-Tier. DB Event ID: {data.get('db_event_id')}"
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"// BACKEND FORWARD ERROR: {response.text}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"// MOCK EMIT ERROR: Redis offline, backend forward failed: {str(e)}"
            )

@router.get("/health")
async def mock_health():
    return {"status": "ok", "mode": "local-mock-development"}

@router.get("/.netlify/functions/stats")
async def mock_netlify_stats():
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{APP_TIER_URL}/health/telemetry", timeout=1.0)
            if res.status_code == 200:
                data = res.json()
                return {
                    "cpu": data.get("cpu_usage", 12.0),
                    "ram": data.get("ram_usage", 34.0),
                    "ping": 1,
                    "fileCount": data.get("events_count", 0) + data.get("contacts_count", 0),
                    "workspaceSizeMB": round(data.get("db_size_kb", 0) / 1024, 2),
                    "wsConnections": data.get("ws_connections", 0)
                }
        except Exception:
            pass

    import random
    return {
        "cpu": round(15 + random.uniform(-2, 2), 1),
        "ram": round(42 + random.uniform(-1, 1), 1),
        "ping": 999,
        "fileCount": 0,
        "workspaceSizeMB": 0.0,
        "wsConnections": 0
    }

class NetlifyJarvisRequest(BaseModel):
    messages: list

@router.post("/.netlify/functions/jarvis")
async def mock_netlify_jarvis(payload: NetlifyJarvisRequest):
    messages = payload.messages
    user_msg = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_msg = msg.get("content", "")
            break
            
    if not user_msg:
        user_msg = "Hello, JARVIS"
        
    print(f"[MOCK-JARVIS] Forwarding chat query to App-Tier: '{user_msg}'")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{APP_TIER_URL}/ai/claude",
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 1000,
                    "system": "You are JARVIS v40.0, Dima's elite personal workstation assistant. Keep your response brief, precise, and highly technical. Answer in Russian or English depending on user input.",
                    "messages": [{"role": "user", "content": user_msg}]
                },
                timeout=15.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "content": [{"text": f"// ERROR: App-Tier responded with status {response.status_code}"}],
                    "usage": {"input_tokens": 0, "output_tokens": 0}
                }
        except Exception as e:
            print(f"[MOCK-JARVIS] Connection to App-Tier failed: {e}")
            return {
                "content": [{"text": "// CONNECTION FALLBACK: Central app-tier core is offline. Please start uvicorn backend to restore cognitive processing."}],
                "usage": {"input_tokens": 0, "output_tokens": 0}
            }

