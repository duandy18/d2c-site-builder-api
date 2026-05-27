from fastapi.testclient import TestClient

from app.main import app


def test_system_health() -> None:
    client = TestClient(app)

    response = client.get("/system/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "d2c-site-builder-api",
        "status": "ok",
    }


def test_admin_health() -> None:
    client = TestClient(app)

    response = client.get("/admin/site-builder/health")

    assert response.status_code == 200
    assert response.json()["service"] == "d2c-site-builder-api"
    assert response.json()["status"] == "ok"


def test_runtime_health() -> None:
    client = TestClient(app)

    response = client.get("/runtime/site-builder/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "d2c-site-builder-runtime",
        "status": "ok",
    }
