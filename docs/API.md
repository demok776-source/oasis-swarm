# REST & WebSocket API Specification

## WebSockets

### `/sync/ws`
- **Method:** `WS`
- **Description:** Subscribes the client to real-time sync layer events from Redis Pub/Sub.
- **Example Payload Received:**
```json
{
  "source": "Redis-PubSub",
  "module": "OASIS_PRIME",
  "event": "DRONE_TELEMETRY_UPDATE",
  "payload": {"altitude": 420.5, "velocity": 45.2}
}
```

## REST Endpoints

### `GET /health/telemetry`
Returns the current system health and component metrics.
**Response:**
```json
{
  "status": "ONLINE",
  "cpu_usage": 32.5,
  "ram_usage": 45.1,
  "db_size_kb": 1024,
  "ws_connections": 5,
  "contacts_count": 12,
  "events_count": 4092,
  "redis_status": "ONLINE",
  "qdrant_status": "ONLINE"
}
```

### `POST /ai/query`
Sends a natural language query to the LangGraph AI Agent.
**Headers:** `x-api-key: <OPENAI_API_KEY>`
**Request:**
```json
{
  "query": "What is the status of the aerospace module?",
  "collection": "oasis_docs",
  "session_id": "web"
}
```
**Response:**
```json
{
  "status": "success",
  "agent_response": "The aerospace module is currently simulating altitude at 42,000 ft."
}
```

## 2. WebSocket Connections

### `ws://localhost:8080/sync/ws/{client_id}`
Connects a client (Web or Unity) to the global event bus.
- **Client -> Server**: Sends JSON payload `{ "event": "player_move", "data": { "x": 10, "y": 0, "z": 5 } }`
- **Server -> Client**: Broadcasts events across all subscribed clients via Redis.
