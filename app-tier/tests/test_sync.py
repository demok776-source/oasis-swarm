from fastapi.testclient import TestClient
from src.main import app
import json

client = TestClient(app)

def test_sync_publish_endpoint():
    payload = {
        "module": "TEST_MODULE",
        "event": "UNIT_TEST",
        "payload": {"data": "test"}
    }
    response = client.post("/sync/publish", json=payload)
    # Could be 200 (if Redis online) or fall back to DB dry_run
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["module"] == "TEST_MODULE"
    assert data["event"] == "UNIT_TEST"

def test_websocket_connect(monkeypatch):
    # Force the synchronous local-fallback broadcast path (see
    # ConnectionManager.broadcast in src/routes/sync.py): TestClient's
    # anyio portal doesn't reliably interleave scheduling for the
    # background `redis_ws_relay_loop` asyncio task alongside a test's
    # synchronous send/receive calls, which made this test flaky/hanging
    # once broadcast() started publishing through Redis instead of
    # sending directly. The actual cross-process Redis relay path is
    # exercised for real in tests/test_cross_process_broadcast.py, which
    # spins up two independent uvicorn processes -- something TestClient
    # can't do, and a stronger test of the real behavior than mocking
    # would be anyway.
    import src.routes.sync as sync_module
    monkeypatch.setattr(sync_module, "redis_client", None)

    with client.websocket_connect("/sync/ws") as websocket:
        test_msg = {"source": "test", "module": "TEST_MODULE", "event": "PING", "payload": {}}
        websocket.send_json(test_msg)

        data = websocket.receive_json()
        assert data["module"] == "TEST_MODULE"
        assert data["event"] == "PING"
