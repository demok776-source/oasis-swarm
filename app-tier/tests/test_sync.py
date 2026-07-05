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

def test_websocket_connect():
    with client.websocket_connect("/sync/ws") as websocket:
        # Send a test message
        test_msg = {"source": "test", "module": "TEST_MODULE", "event": "PING", "payload": {}}
        websocket.send_json(test_msg)
        
        # Receive broadcast
        data = websocket.receive_json()
        assert data["module"] == "TEST_MODULE"
        assert data["event"] == "PING"
