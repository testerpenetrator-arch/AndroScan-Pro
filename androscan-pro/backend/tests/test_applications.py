import io
import zipfile

from fastapi.testclient import TestClient

from app.main import app
from app.services.apk_storage import S3ObjectStorage


def login(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@androscan.dev", "password": "Password123!"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def make_apk() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("AndroidManifest.xml", b"binary-manifest-placeholder")
        archive.writestr("classes.dex", b"dex-placeholder")
        archive.writestr("resources.arsc", b"resources-placeholder")
        archive.writestr("res/values/strings.xml", b"<resources/>")
    return buffer.getvalue()


def test_create_application_and_list_versions(monkeypatch):
    monkeypatch.setattr(S3ObjectStorage, "put_fileobj", lambda *args, **kwargs: None)
    client = TestClient(app)
    headers = login(client)

    org = client.post(
        "/api/v1/organizations",
        json={"name": "F93 Empresa", "slug": "f93-empresa"},
        headers=headers,
    )
    assert org.status_code == 201
    organization_id = org.json()["id"]

    created = client.post(
        f"/api/v1/organizations/{organization_id}/applications",
        json={"name": "Aplicación Demo", "package_name": "com.example.androscan"},
        headers=headers,
    )
    assert created.status_code == 201
    application_id = created.json()["id"]

    apk = client.post(
        f"/api/v1/organizations/{organization_id}/applications/{application_id}/apk",
        files={"file": ("demo.apk", make_apk(), "application/vnd.android.package-archive")},
        data={"version_name": "1.0.0", "version_code": "1"},
        headers=headers,
    )
    assert apk.status_code == 201
    payload = apk.json()
    assert payload["application_id"] == application_id
    assert payload["validation_status"] == "VALIDATED"
    assert len(payload["sha256"]) == 64
    assert payload["metadata_json"]["zip_entries"] == 4

    versions = client.get(
        f"/api/v1/organizations/{organization_id}/applications/{application_id}/versions",
        headers=headers,
    )
    assert versions.status_code == 200
    assert len(versions.json()) == 1


def test_duplicate_sha256_is_rejected(monkeypatch):
    monkeypatch.setattr(S3ObjectStorage, "put_fileobj", lambda *args, **kwargs: None)
    client = TestClient(app)
    headers = login(client)

    org = client.post(
        "/api/v1/organizations",
        json={"name": "F93 Duplicate", "slug": "f93-duplicate"},
        headers=headers,
    )
    organization_id = org.json()["id"]
    created = client.post(
        f"/api/v1/organizations/{organization_id}/applications",
        json={"name": "Duplicate App", "package_name": "com.example.duplicate"},
        headers=headers,
    )
    application_id = created.json()["id"]
    content = make_apk()

    first = client.post(
        f"/api/v1/organizations/{organization_id}/applications/{application_id}/apk",
        files={"file": ("one.apk", content, "application/vnd.android.package-archive")},
        headers=headers,
    )
    assert first.status_code == 201

    second = client.post(
        f"/api/v1/organizations/{organization_id}/applications/{application_id}/apk",
        files={"file": ("two.apk", content, "application/vnd.android.package-archive")},
        headers=headers,
    )
    assert second.status_code == 409


def test_invalid_apk_is_rejected(monkeypatch):
    monkeypatch.setattr(S3ObjectStorage, "put_fileobj", lambda *args, **kwargs: None)
    client = TestClient(app)
    headers = login(client)

    org = client.post(
        "/api/v1/organizations",
        json={"name": "F93 Invalid", "slug": "f93-invalid"},
        headers=headers,
    )
    organization_id = org.json()["id"]
    created = client.post(
        f"/api/v1/organizations/{organization_id}/applications",
        json={"name": "Invalid App", "package_name": "com.example.invalid"},
        headers=headers,
    )
    application_id = created.json()["id"]

    response = client.post(
        f"/api/v1/organizations/{organization_id}/applications/{application_id}/apk",
        files={"file": ("bad.apk", b"not-an-apk", "application/vnd.android.package-archive")},
        headers=headers,
    )
    assert response.status_code == 422


def test_application_is_tenant_isolated(monkeypatch):
    monkeypatch.setattr(S3ObjectStorage, "put_fileobj", lambda *args, **kwargs: None)
    client = TestClient(app)
    admin_headers = login(client)

    org_a = client.post(
        "/api/v1/organizations",
        json={"name": "F93 Tenant A", "slug": "f93-tenant-a"},
        headers=admin_headers,
    ).json()["id"]
    org_b = client.post(
        "/api/v1/organizations",
        json={"name": "F93 Tenant B", "slug": "f93-tenant-b"},
        headers=admin_headers,
    ).json()["id"]

    app_b = client.post(
        f"/api/v1/organizations/{org_b}/applications",
        json={"name": "Private App", "package_name": "com.example.private"},
        headers=admin_headers,
    ).json()["id"]

    user = client.post(
        f"/api/v1/organizations/{org_a}/users",
        json={"email": "f93-tenant-user@androscan.dev", "full_name": "Tenant User", "password": "Tenant123!"},
        headers=admin_headers,
    )
    assert user.status_code == 201
    user_login = client.post(
        "/api/v1/auth/login",
        json={"email": "f93-tenant-user@androscan.dev", "password": "Tenant123!"},
    )
    user_headers = {"Authorization": f"Bearer {user_login.json()['access_token']}"}

    denied = client.get(
        f"/api/v1/organizations/{org_b}/applications/{app_b}",
        headers=user_headers,
    )
    assert denied.status_code == 403
