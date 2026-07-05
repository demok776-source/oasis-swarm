# OASIS SYSTEM CORE - Production Runbook

## 1. Overview
This runbook provides operational instructions for managing the 13-module OASIS ecosystem in a production environment.

## 2. Telemetry Sync Layer Failures
If the Sync Layer (Redis) goes offline:
- **Symptom:** `/sync/publish` endpoints return `"status": "dry_run"` and log `Redis client offline`.
- **Action:** Ensure the Redis container/instance is reachable. The FastAPI backend will automatically queue events into the PostgreSQL `sync_events` table as a fallback. Once Redis is restored, these can be replayed.

## 3. JARVIS Self-Healing & Critical Failures
JARVIS is permanently connected to the Sync Layer.
- **Symptom:** `CRITICAL_FAILURE` payloads broadcasted by any module (e.g. OASIS_PRIME Unity crash).
- **Action:** JARVIS will intercept this event and attempt to restart the component via its `trigger_self_healing` tool. Check `docker logs oasis-app-tier-1` to verify the JSON structured log output for agent intervention.

## 4. Qdrant & OpenAI API Limits
- **Symptom:** `HTTP Error 429: Too Many Requests` from OpenAI API.
- **Action:** The system safely falls back to a deterministic local mock vector generator. RAG engine will still return results based on exact keyword overlap or mock distances. Consider upgrading OpenAI tier limits.

## 5. UI Animations & Frontend Performance
- **Symptom:** Next.js UI drops frames on `Noteboard` or `Master-Plan`.
- **Action:** Framer Motion transitions are set to `layoutId` sharing. If the DOM nodes exceed 1000 items on the Noteboard, consider adding pagination to the UI layer to keep FPS at 60.
