"""Verifies the new security layer (src/security.py) actually does what it
claims: rate limiting returns 429 once exceeded, and API-key auth actually
rejects bad/missing keys when APP_API_KEY is configured."""
import importlib
import os

import pytest
from fastapi.testclient import TestClient


def test_rate_limit_returns_429_when_exceeded(monkeypatch):
    # Fresh import with a tiny limit so the test doesn't need 30+ requests.
    monkeypatch.delenv("APP_API_KEY", raising=False)
    import src.security as security_module
    importlib.reload(security_module)

    from fastapi import FastAPI, Request
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    app = FastAPI()
    app.state.limiter = security_module.limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.get("/limited")
    @security_module.limiter.limit("2/minute")
    def limited_endpoint(request: Request):
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200
    third = client.get("/limited")
    assert third.status_code == 429


def test_require_api_key_blocks_wrong_key(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "correct-horse-battery-staple")
    import src.security as security_module
    importlib.reload(security_module)

    from fastapi import FastAPI, Depends

    app = FastAPI()
    app.state.limiter = security_module.limiter

    @app.get("/protected", dependencies=[Depends(security_module.require_api_key)])
    def protected_endpoint():
        return {"secret": True}

    client = TestClient(app)
    assert client.get("/protected").status_code == 401
    assert client.get("/protected", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/protected", headers={"X-API-Key": "correct-horse-battery-staple"}).status_code == 200


def test_require_api_key_noop_when_unset(monkeypatch):
    monkeypatch.delenv("APP_API_KEY", raising=False)
    import src.security as security_module
    importlib.reload(security_module)

    from fastapi import FastAPI, Depends

    app = FastAPI()
    app.state.limiter = security_module.limiter

    @app.get("/protected", dependencies=[Depends(security_module.require_api_key)])
    def protected_endpoint():
        return {"secret": True}

    client = TestClient(app)
    # No APP_API_KEY configured -> auth is a documented no-op, not a silent 500.
    assert client.get("/protected").status_code == 200
