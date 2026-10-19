from fastapi.testclient import TestClient
from app.main import app


def _admin_headers(client):
    login = client.post("/api/v1/auth/login", json={"email": "admin@androscan.dev", "password": "Password123!"})
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _organization(client, headers, slug):
    response = client.post("/api/v1/organizations", json={"name": f"Admin {slug}", "slug": slug}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_admin_settings_defaults_and_update():
    client = TestClient(app); headers = _admin_headers(client)
    org_id = _organization(client, headers, "f912-settings")
    default = client.get(f"/api/v1/organizations/{org_id}/admin/settings", headers=headers)
    assert default.status_code == 200, default.text
    assert default.json()["max_apk_size_mb"] == 100
    assert default.json()["external_ai_enabled"] is False
    updated = client.put(f"/api/v1/organizations/{org_id}/admin/settings", json={"max_apk_size_mb": 50, "ai_assistance_enabled": False}, headers=headers)
    assert updated.status_code == 200, updated.text
    assert updated.json()["max_apk_size_mb"] == 50
    assert updated.json()["ai_assistance_enabled"] is False


def test_admin_settings_reject_invalid_ranges():
    client = TestClient(app); headers = _admin_headers(client)
    org_id = _organization(client, headers, "f912-invalid")
    response = client.put(f"/api/v1/organizations/{org_id}/admin/settings", json={"max_apk_size_mb": 9999}, headers=headers)
    assert response.status_code == 422


def test_tool_policy_update_and_validation():
    client = TestClient(app); headers = _admin_headers(client)
    org_id = _organization(client, headers, "f912-tools")
    updated = client.put(f"/api/v1/organizations/{org_id}/admin/tools", json={"enabled_tools": ["jadx", "mobsf"]}, headers=headers)
    assert updated.status_code == 200, updated.text
    assert set(updated.json()["enabled_tools"]) == {"jadx", "mobsf"}
    invalid = client.put(f"/api/v1/organizations/{org_id}/admin/tools", json={"enabled_tools": ["unknown-tool"]}, headers=headers)
    assert invalid.status_code == 422


def test_admin_routes_enforce_membership():
    client = TestClient(app); headers = _admin_headers(client)
    response = client.get("/api/v1/organizations/00000000-0000-0000-0000-000000000000/admin/settings", headers=headers)
    assert response.status_code in (403, 404)
