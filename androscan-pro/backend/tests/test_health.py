from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "AndroScan API"


def test_request_trace_id_is_returned() -> None:
    response = client.get("/api/v1/health", headers={"X-Trace-Id": "test-trace-123"})
    assert response.status_code == 200
    assert response.headers["X-Trace-Id"] == "test-trace-123"


def test_invalid_trace_id_is_replaced() -> None:
    response = client.get("/api/v1/health", headers={"X-Trace-Id": "bad trace id\n"})
    assert response.status_code == 200
    assert response.headers.get("X-Trace-Id")
    assert " " not in response.headers["X-Trace-Id"]


def test_liveness_endpoint() -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_endpoint_checks_database() -> None:
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"
