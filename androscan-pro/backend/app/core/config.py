from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración centralizada de AndroScan."""

    app_name: str = "AndroScan API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    jwt_secret_key: str = "development-secret-change-me-32-bytes!!"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "postgresql+psycopg://androscan:androscan@localhost:5432/androscan"
    redis_url: str = "redis://localhost:6379/0"

    storage_backend: str = "local"  # local para el MVP; s3 para almacenamiento compatible S3
    local_storage_path: str = "/data/apks"
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "androscan"
    s3_secret_key: str = "androscan-development-only"
    s3_bucket: str = "androscan-apks"
    s3_region: str = "us-east-1"

    # Límite operativo provisional; el valor definitivo queda sujeto a DP-009.
    max_apk_size_mb: int = 100

    # Límites F9.5; valores iniciales operativos, sujetos a DP-014/DP-015.
    sandbox_image: str = "androscan/sandbox-tools:0.1"
    sandbox_cpu: float = 1.0
    sandbox_memory_mb: int = 1024
    sandbox_pids: int = 128
    sandbox_timeout_seconds: int = 900
    sandbox_storage_mb: int = 2048

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
