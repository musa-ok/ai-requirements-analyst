"""FastAPI boot ve health endpoint smoke testleri (agir import yok)."""

from fastapi.testclient import TestClient


def test_root_returns_ok():
    from backend.main import app

    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_ok():
    from backend.main import app

    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
