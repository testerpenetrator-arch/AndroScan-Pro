from app.main import app


def test_comparison_endpoint_is_registered():
    paths = app.openapi()["paths"]
    assert "/api/v1/organizations/{organization_id}/comparisons" in paths
    assert "post" in paths["/api/v1/organizations/{organization_id}/comparisons"]
