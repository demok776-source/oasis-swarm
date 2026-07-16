import socket
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def _ollama_reachable() -> bool:
    """These two tests exercise real LLM routing and need a live Ollama
    instance (see docker-compose.yml: service `ollama`, host `ollama:11434`).
    Skip them instead of silently failing when running outside that stack
    (e.g. plain `pytest` on a laptop, or a CI job without the compose stack up)."""
    try:
        socket.getaddrinfo("ollama", 11434)
        return True
    except socket.gaierror:
        return False


requires_ollama = pytest.mark.skipif(
    not _ollama_reachable(),
    reason="Ollama host unreachable — run via docker-compose to exercise real LLM routing",
)


@requires_ollama
def test_query_ai_swarm_data():
    payload = {
        "query": "What is OASIS?",
        "module": "TEST"
    }
    response = client.post("/ai/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "[DataAgent]" in data["response"]


@requires_ollama
def test_query_ai_swarm_devops():
    payload = {
        "query": "Please heal the system, it is critical",
        "module": "TEST"
    }
    response = client.post("/ai/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "[DevOpsAgent]" in data["response"]
