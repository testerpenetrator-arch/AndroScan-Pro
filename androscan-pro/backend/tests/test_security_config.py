from types import SimpleNamespace

import pytest

from app.core.security_config import validate_production_secrets


def settings(jwt="a" * 64, s3="b" * 48):
    return SimpleNamespace(jwt_secret_key=jwt, s3_secret_key=s3)


def test_accepts_long_random_secrets():
    validate_production_secrets(settings())


@pytest.mark.parametrize("jwt", ["", "change-me", "development-secret-change-me-32-bytes!!", "short"])
def test_rejects_missing_default_or_short_jwt(jwt):
    with pytest.raises(RuntimeError):
        validate_production_secrets(settings(jwt=jwt))


def test_rejects_default_s3_secret():
    with pytest.raises(RuntimeError):
        validate_production_secrets(settings(s3="androscan-development-only"))
