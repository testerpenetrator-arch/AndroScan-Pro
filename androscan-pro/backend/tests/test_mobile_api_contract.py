"""Contratos mínimos de API requeridos por el cliente Android."""
from app.main import app


def test_android_authentication_and_organization_routes_exist():
    paths = app.openapi()["paths"]
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/organizations" in paths


def test_android_application_upload_routes_exist():
    paths = app.openapi()["paths"]
    assert "/api/v1/organizations/{organization_id}/applications" in paths
    assert "/api/v1/organizations/{organization_id}/applications/{application_id}/apk" in paths
    assert "/api/v1/organizations/{organization_id}/applications/{application_id}/analyses" in paths


def test_android_analysis_and_findings_routes_exist():
    paths = app.openapi()["paths"]
    assert "/api/v1/organizations/{organization_id}/versions/{version_id}/analyses" in paths
    assert "/api/v1/organizations/{organization_id}/analyses/{analysis_id}/findings" in paths


def test_android_report_routes_exist():
    paths = app.openapi()["paths"]
    assert "/api/v1/organizations/{organization_id}/reports" in paths
    assert "/api/v1/organizations/{organization_id}/reports/{report_id}/download" in paths
