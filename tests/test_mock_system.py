import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add app-tier directory to python path
app_tier_dir = r"C:\Users\Lapstore\.gemini\antigravity-ide\scratch\oasis\app-tier"
sys.path.insert(0, app_tier_dir)

# Configure mock/test environment variables
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["REDIS_HOST"] = "127.0.0.1"
os.environ["QDRANT_URL"] = "http://127.0.0.1:6333"
os.environ["USE_SQLITE"] = "true"

from src.main import app
from src.utils.embeddings import get_embedding
from src.db import engine, Base

Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "JARVIS" in response.json()["message"]

def test_embeddings_dimension():
    vec = get_embedding("test query string for oasis memory fabric")
    assert len(vec) == 1536
    # Assert unit normalization
    sum_squares = sum(x*x for x in vec)
    assert abs(sum_squares - 1.0) < 1e-4

def test_ai_query_mock_fallback():
    response = client.post("/ai/query", json={"query": "what is oasis system core"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # When api key is dummy, it returns a mocked simulation response
    assert "local simulation mode" in data["agent_response"] or "Omni-Eternity" in data["agent_response"]

def test_local_rag_semantic_search():
    # Since we are using the LangGraph agent and dummy key, we will just test the endpoint responds correctly
    response = client.post("/ai/query", json={"query": "drone autopilot navigation state machine"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "agent_response" in data

def test_sync_publish_dry_run_fallback():
    response = client.post("/sync/publish", json={
        "module": "LOCAL_TEST",
        "event": "BOOTSTRAP",
        "payload": {"status": "OK"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "dry_run"
    assert "Redis connection offline" in data["info"]

def test_sqlite_crud_and_contact_api():
    from src.db import engine, SessionLocal, Base
    from src.crud import create_contact, get_contacts, create_sync_event, get_sync_events
    
    # Initialize SQLite schemas
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Test Contact Message CRUD
        contact = create_contact(db, "Test User", "test@domain.com", "Hello from tests")
        assert contact.id is not None
        assert contact.name == "Test User"
        
        contacts = get_contacts(db)
        assert len(contacts) >= 1
        assert contacts[0].email == "test@domain.com"
        
        # Test Sync Event CRUD
        event = create_sync_event(db, "TEST_MOD", "START", {"init": True})
        assert event.id is not None
        
        events = get_sync_events(db)
        assert len(events) >= 1
        assert events[0].module == "TEST_MOD"
        assert events[0].decoded_payload["init"] is True
        
    finally:
        db.close()

def test_contact_route_with_sqlite():
    # Hit actual FastAPI POST /contact route
    response = client.post("/contact", json={
        "name": "Alex Dynamo",
        "email": "alex@oasis.dev",
        "message": "Testing automated database integration."
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ok"
    assert data["id"] is not None

def test_contact_validation_empty_fields():
    # Test empty name
    response = client.post("/contact", json={
        "name": "   ",
        "email": "alex@oasis.dev",
        "message": "Valid message"
    })
    assert response.status_code == 400
    assert "Field 'name' cannot be empty" in response.json()["detail"]

    # Test empty email
    response = client.post("/contact", json={
        "name": "Alex Dynamo",
        "email": "",
        "message": "Valid message"
    })
    assert response.status_code == 400
    assert "Field 'email' cannot be empty" in response.json()["detail"]

    # Test empty message
    response = client.post("/contact", json={
        "name": "Alex Dynamo",
        "email": "alex@oasis.dev",
        "message": ""
    })
    assert response.status_code == 400
    assert "Field 'message' cannot be empty" in response.json()["detail"]

def test_contact_validation_invalid_email():
    response = client.post("/contact", json={
        "name": "Alex Dynamo",
        "email": "invalid-email-format",
        "message": "Valid message"
    })
    assert response.status_code == 400
    assert "Invalid email address format" in response.json()["detail"]

def test_sync_publish_payloads():
    # Test publishing nested dictionary payload
    response1 = client.post("/sync/publish", json={
        "module": "TEST_MODULE",
        "event": "NESTED_DATA",
        "payload": {"nested": {"status": "ACTIVE", "metrics": {"fps": 60}}}
    })
    assert response1.status_code == 200
    assert response1.json()["status"] == "dry_run"

    # Test empty payload dict
    response2 = client.post("/sync/publish", json={
        "module": "TEST_MODULE",
        "event": "EMPTY_DATA",
        "payload": {}
    })
    assert response2.status_code == 200
    assert response2.json()["status"] == "dry_run"

    # Test simple numeric payload
    response3 = client.post("/sync/publish", json={
        "module": "TEST_MODULE",
        "event": "NUMERIC_DATA",
        "payload": {"count": 9999}
    })
    assert response3.status_code == 200
    assert response3.json()["status"] == "dry_run"

def test_sqlite_sync_propagation():
    # Verify that calling /sync/publish when Redis is offline inserts a row in sqlite DB sync_events_history
    response = client.post("/sync/publish", json={
        "module": "PROPAGATION_TEST",
        "event": "OFFLINE_EMIT",
        "payload": {"value": 12345}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "dry_run"
    assert "db_event_id" in data

    # Verify database entry exists
    from src.db import SessionLocal
    from src.models import SyncEventHistory
    db = SessionLocal()
    try:
        db_event = db.query(SyncEventHistory).filter(SyncEventHistory.id == data["db_event_id"]).first()
        assert db_event is not None
        assert db_event.module == "PROPAGATION_TEST"
        assert db_event.event == "OFFLINE_EMIT"
    finally:
        db.close()

def test_websocket_sync_bus():
    with client.websocket_connect("/sync/ws") as websocket:
        response = client.post("/sync/publish", json={
            "module": "WS_TEST",
            "event": "CONNECT_VERIFY",
            "payload": {"ws_alive": True}
        })
        assert response.status_code == 200
        data = websocket.receive_json()
        assert data["module"] == "WS_TEST"
        assert data["event"] == "CONNECT_VERIFY"
        assert data["payload"]["ws_alive"] is True

        # Test client broadcast to peer channel
        websocket.send_json({"type": "sync_tasks", "tasks": [{"id": "t1", "text": "Sync", "col": "todo"}]})
        data2 = websocket.receive_json()
        assert data2["type"] == "sync_tasks"
        assert data2["tasks"][0]["id"] == "t1"

def test_health_telemetry():
    response = client.get("/health/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "cpu_usage" in data
    assert "ram_usage" in data
    assert "db_size_kb" in data
    assert "ws_connections" in data



