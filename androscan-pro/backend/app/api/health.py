from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Estado de la API")
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
    )
