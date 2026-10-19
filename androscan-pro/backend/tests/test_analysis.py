from fastapi.testclient import TestClient

from app.main import app


def test_analysis_state_machine():
    from app.services.analysis_orchestrator import TRANSITIONS

    assert "QUEUED" in TRANSITIONS["CREATED"]
    assert "PREPARING" in TRANSITIONS["QUEUED"]
    assert "RUNNING" in TRANSITIONS["PREPARING"]
    assert "COMPLETED" in TRANSITIONS["PROCESSING_RESULTS"]
    assert not TRANSITIONS["COMPLETED"]


def test_analysis_endpoint_requires_authentication():
    client = TestClient(app)
    response = client.post(
        "/api/v1/organizations/nonexistent/versions/nonexistent/analyses",
        json={},
    )
    assert response.status_code == 401
