"""Test the health-check endpoint through the HTTP layer."""
from __future__ import annotations

from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.routes.health_routes import router as health_router
from fastapi import FastAPI


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(health_router)
    return TestClient(app)


def test_health_returns_ok():
    response = _client().get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == get_settings().app_name
