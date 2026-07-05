# OASIS SYSTEM CORE vMAX - Modules Overview

The ecosystem is decoupled into 13 autonomous modules. Below are the primary technical boundaries:

## 1. App-Tier (FastAPI Backend)
Central routing and event processing hub.
- **`src/routes/ai.py`**: LangGraph agent integration and tool routing.
- **`src/routes/sync.py`**: WebSocket manager for real-time telemetry streaming.
- **`src/db.py`**: SQLAlchemy ORM mappings to PostgreSQL.
- **`src/qdrant.py`**: Vector database client initialization.

## 2. Frontend Layer (Next.js - oasis-v5)
The primary human-interface dashboard.
- **`/compute`**: Real-time server telemetry.
- **`/memory`**: Database relational and vector metrics.
- **`/aerospace`**: Simulated drone uplink visualization.
- **`/settings`**: Local secure storage for AI API keys.

## 3. OASIS PRIME (Unity Game Module)
The 3D interactive simulation layer.
- **ECS Core**: Entity Component System for high-performance object rendering.
- **Procedural Generation**: Infinite terrain generation using Perlin Noise.
- **Network Sync**: Unity WebSockets connecting to `App-Tier` for shared state synchronization across clients.

## 4. Sync Layer (Event Bus)
High-throughput event streaming.
- Built on Redis Pub/Sub (capable of scaling to Kafka for 10k+ EPS).
- Provides Event Replay and state hydration for newly connected clients.
