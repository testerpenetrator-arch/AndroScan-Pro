from fastapi.testclient import TestClient
from app.main import app


def test_tool_execution_endpoint_requires_authentication():
    client = TestClient(app)
    response = client.get("/api/v1/organizations/nonexistent/analyses/nonexistent/tools")
    assert response.status_code == 401
