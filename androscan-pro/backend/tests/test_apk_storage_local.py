from io import BytesIO
from types import SimpleNamespace

import pytest

from app.services import apk_storage
from app.services.apk_storage import ObjectStorageError, S3ObjectStorage


@pytest.fixture
def local_storage(tmp_path, monkeypatch):
    settings = SimpleNamespace(
        storage_backend="local",
        local_storage_path=str(tmp_path / "apks"),
        s3_bucket="androscan-apks",
        s3_endpoint="http://unused",
        s3_access_key="unused",
        s3_secret_key="unused",
        s3_region="us-east-1",
    )
    monkeypatch.setattr(apk_storage, "get_settings", lambda: settings)
    return S3ObjectStorage()


def test_local_storage_round_trip(local_storage, tmp_path):
    payload = b"sample apk bytes"
    local_storage.put_fileobj(
        "organizations/org1/applications/app1/sample.apk",
        BytesIO(payload),
        content_type="application/vnd.android.package-archive",
        content_length=len(payload),
    )
    destination = tmp_path / "downloaded.apk"
    local_storage.download_to_file(
        "organizations/org1/applications/app1/sample.apk", str(destination)
    )
    assert destination.read_bytes() == payload


def test_local_storage_rejects_path_traversal(local_storage):
    with pytest.raises(ObjectStorageError):
        local_storage.put_fileobj(
            "../../outside.apk", BytesIO(b"bad"), content_type="application/octet-stream", content_length=3
        )
