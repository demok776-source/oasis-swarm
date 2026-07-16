"""
Regression test for the cross-worker WebSocket broadcast fix in
src/routes/sync.py (ConnectionManager.broadcast + redis_ws_relay_loop).

Background: gunicorn_conf.py runs multiple worker PROCESSES
(cpu_count() * 2), each with its own independent Python memory. Before this
fix, ConnectionManager.broadcast() only iterated the CURRENT process's own
in-memory `active_connections` list -- a client connected to worker A would
never see a broadcast published via worker B. This is exactly the scenario
TestClient cannot exercise (it runs the whole app in one process/portal),
so this test spins up two real uvicorn subprocesses against a real Redis
instance instead.

Skipped automatically if Redis isn't reachable (e.g. plain `pytest` on a
laptop without `docker-compose up redis`).
"""
import asyncio
import json
import os
import socket
import subprocess
import sys
import time

import httpx
import pytest
import websockets


def _redis_reachable() -> bool:
    host = os.environ.get("REDIS_HOST", "127.0.0.1")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False


requires_redis = pytest.mark.skipif(
    not _redis_reachable(),
    reason="Redis unreachable -- this test needs a real broker to prove cross-process relay works",
)


def _wait_for_server(port: int, timeout_s: float = 30.0) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            httpx.get(f"http://127.0.0.1:{port}/", timeout=2.0)
            return True
        except httpx.HTTPError:
            time.sleep(0.5)
    return False


@requires_redis
def test_cross_process_broadcast():
    env = dict(os.environ)
    env["USE_SQLITE"] = "true"

    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_a = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8195"],
        cwd=app_dir, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    proc_b = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8196"],
        cwd=app_dir, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        assert _wait_for_server(8195), "worker A never came up"
        assert _wait_for_server(8196), "worker B never came up"

        async def run():
            async with websockets.connect("ws://127.0.0.1:8195/sync/ws") as ws_a:
                await asyncio.sleep(0.3)
                async with httpx.AsyncClient() as http:
                    resp = await http.post(
                        "http://127.0.0.1:8196/sync/publish",
                        json={"module": "CROSS_WORKER_TEST", "event": "PING_FROM_B", "payload": {}},
                    )
                    assert resp.status_code == 200

                msg = await asyncio.wait_for(ws_a.recv(), timeout=10)
                data = json.loads(msg)
                assert data["module"] == "CROSS_WORKER_TEST"
                assert data["event"] == "PING_FROM_B"

        asyncio.run(run())
    finally:
        proc_a.terminate()
        proc_b.terminate()
        proc_a.wait(timeout=5)
        proc_b.wait(timeout=5)
