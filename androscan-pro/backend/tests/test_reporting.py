import json
from types import SimpleNamespace
from app.services.reporting import build_report_data, render_report, sha256_bytes


def sample_data():
    app = SimpleNamespace(id="app-1", name="Demo <App>", package_name="com.example.demo")
    version = SimpleNamespace(id="ver-1", original_filename="demo.apk", sha256="a" * 64, size_bytes=123, version_name="1.0", version_code="1")
    analysis = SimpleNamespace(id="analysis-1", state="COMPLETED", trace_id="trace-1", created_at=None, started_at=None, finished_at=None)
    finding = SimpleNamespace(id="finding-1", correlation_key="rule:key", rule_id="MASVS-STORAGE-1", title="Cleartext secret", description="Secret stored in plain text", category="STORAGE", severity="HIGH", priority="P1", review_state="PENDING", analyst_notes=None, evidence_json={"file": "x"}, raw_result_ref=None, tool_execution_id="tool-1", created_at=None)
    tool = SimpleNamespace(id="tool-1", tool_name="JADX", tool_version="1.5.3", state="COMPLETED", exit_code=0)
    return build_report_data("org-1", analysis, version, app, [finding], [tool])


def test_json_report_contains_provenance_and_disclaimer():
    data = sample_data()
    content_type, ext, raw = render_report(data, "JSON")
    parsed = json.loads(raw)
    assert content_type == "application/json" and ext == "json"
    assert parsed["findings"][0]["tool_execution_id"] == "tool-1"
    assert parsed["summary"]["by_severity"]["HIGH"] == 1
    assert "analista humano" in parsed["disclaimer"]
    assert len(sha256_bytes(raw)) == 64


def test_html_report_escapes_untrusted_app_name():
    data = sample_data()
    content_type, ext, raw = render_report(data, "HTML")
    body = raw.decode("utf-8")
    assert content_type.startswith("text/html") and ext == "html"
    assert "Demo &lt;App&gt;" in body
    assert "<App>" not in body


def test_pdf_report_has_pdf_signature():
    content_type, ext, raw = render_report(sample_data(), "PDF")
    assert content_type == "application/pdf" and ext == "pdf"
    assert raw.startswith(b"%PDF-")


def test_report_api_create_list_and_download_json(monkeypatch):
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
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    org_resp = client.post("/api/v1/organizations", json={"name": "F910 Reports Org", "slug": "f910-reports-org"}, headers=headers)
    assert org_resp.status_code == 201
    org_id = org_resp.json()["id"]
    app_resp = client.post(f"/api/v1/organizations/{org_id}/applications", json={"name": "Reports Demo", "package_name": "com.example.reportsdemo"}, headers=headers)
    assert app_resp.status_code == 201
    app_id = app_resp.json()["id"]
    apk_bytes = io.BytesIO()
    with zipfile.ZipFile(apk_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("AndroidManifest.xml", b"manifest")
        zf.writestr("classes.dex", b"dex")
    upload = client.post(f"/api/v1/organizations/{org_id}/applications/{app_id}/apk", files={"file": ("demo.apk", apk_bytes.getvalue(), "application/vnd.android.package-archive")}, headers=headers)
    assert upload.status_code == 201
    version_id = upload.json()["id"]
    analysis_resp = client.post(f"/api/v1/organizations/{org_id}/versions/{version_id}/analyses", json={"trace_id": "f910-test"}, headers=headers)
    assert analysis_resp.status_code == 202
    analysis_id = analysis_resp.json()["id"]
    report_resp = client.post(f"/api/v1/organizations/{org_id}/reports", json={"analysis_id": analysis_id, "format": "JSON"}, headers=headers)
    assert report_resp.status_code == 201, report_resp.text
    report = report_resp.json()
    downloaded = client.get(f"/api/v1/organizations/{org_id}/reports/{report['id']}/download", headers=headers)
    assert downloaded.status_code == 200
    assert downloaded.headers["content-type"].startswith("application/json")
    assert downloaded.headers["x-content-sha256"] == report["sha256"]
    assert json.loads(downloaded.content)["analysis"]["id"] == analysis_id
    listed = client.get(f"/api/v1/organizations/{org_id}/reports?analysis_id={analysis_id}", headers=headers)
    assert listed.status_code == 200 and any(item["id"] == report["id"] for item in listed.json())
