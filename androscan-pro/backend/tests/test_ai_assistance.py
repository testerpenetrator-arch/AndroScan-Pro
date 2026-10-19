from types import SimpleNamespace
from app.services.ai_assistance import DISCLAIMER, draft_assistance


def test_local_assistance_suggests_validation_without_deciding_risk():
    finding = SimpleNamespace(
        id="finding-1", title="Cleartext secret", severity="HIGH", priority="P1",
        review_state="PENDING", description="A possible secret was detected.", category="STORAGE",
    )
    result = draft_assistance([finding])
    assert result["finding_count"] == 1
    assert result["by_severity"]["HIGH"] == 1
    assert result["suggestions"][0]["human_review_required"] is True
    assert result["suggestions"][0]["observed_severity"] == "HIGH"
    assert "almacen" in result["suggestions"][0]["validation_steps"].lower()
    assert "no constituye una conclusión" in result["limitations"][0]


def test_empty_analysis_returns_zero_counts():
    result = draft_assistance([])
    assert result["finding_count"] == 0
    assert result["by_severity"]["CRITICAL"] == 0
    assert result["suggestions"] == []


def test_disclaimer_states_local_processing_and_human_review():
    assert "analista humano" in DISCLAIMER
    assert "no envía APK" in DISCLAIMER


def test_ai_assistance_api_create_and_list(monkeypatch):
    import io
    import zipfile
    from fastapi.testclient import TestClient
    from app.main import app as fastapi_app
    from app.services.apk_storage import S3ObjectStorage
    from app.services.analysis_tasks import queue_analysis_task

    monkeypatch.setattr(S3ObjectStorage, "put_fileobj", lambda *args, **kwargs: None)
    monkeypatch.setattr(queue_analysis_task, "delay", lambda *args, **kwargs: None)
    client = TestClient(fastapi_app)
    login = client.post("/api/v1/auth/login", json={"email": "admin@androscan.dev", "password": "Password123!"})
    assert login.status_code == 200, login.text
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    org_resp = client.post("/api/v1/organizations", json={"name": "F911 AI Org", "slug": "f911-ai-org"}, headers=headers)
    assert org_resp.status_code == 201, org_resp.text
    org_id = org_resp.json()["id"]
    app_resp = client.post(f"/api/v1/organizations/{org_id}/applications", json={"name": "AI Demo", "package_name": "com.example.f911demo"}, headers=headers)
    assert app_resp.status_code == 201, app_resp.text
    app_id = app_resp.json()["id"]
    apk_bytes = io.BytesIO()
    with zipfile.ZipFile(apk_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("AndroidManifest.xml", b"manifest")
        zf.writestr("classes.dex", b"dex")
    upload = client.post(f"/api/v1/organizations/{org_id}/applications/{app_id}/apk", files={"file": ("demo.apk", apk_bytes.getvalue(), "application/vnd.android.package-archive")}, headers=headers)
    assert upload.status_code == 201, upload.text
    analysis = client.post(f"/api/v1/organizations/{org_id}/versions/{upload.json()['id']}/analyses", json={"trace_id": "f911-test"}, headers=headers)
    assert analysis.status_code == 202, analysis.text
    analysis_id = analysis.json()["id"]
    created = client.post(f"/api/v1/organizations/{org_id}/analyses/{analysis_id}/ai-assistance", json={}, headers=headers)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["provider"] == "local-rule-assistant"
    assert body["status"] == "REVIEW_REQUIRED"
    assert "analista humano" in body["disclaimer"]
    listed = client.get(f"/api/v1/organizations/{org_id}/analyses/{analysis_id}/ai-assistance", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == body["id"] for item in listed.json())
