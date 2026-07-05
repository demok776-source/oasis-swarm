from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_query_ai_swarm_data():
    payload = {
        "query": "What is OASIS?",
        "module": "TEST"
    }
    response = client.post("/ai/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "[DataAgent]" in data["response"]

def test_query_ai_swarm_devops():
    payload = {
        "query": "Please heal the system, it is critical",
        "module": "TEST"
    }
    response = client.post("/ai/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "[DevOpsAgent]" in data["response"]
