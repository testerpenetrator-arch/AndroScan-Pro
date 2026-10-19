from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrganizationSettingsUpdate(BaseModel):
    max_apk_size_mb: int | None = Field(default=None, ge=1, le=500)
    max_concurrent_analyses: int | None = Field(default=None, ge=1, le=50)
    analysis_timeout_seconds: int | None = Field(default=None, ge=60, le=3600)
    retention_days: int | None = Field(default=None, ge=1, le=3650)
    ai_assistance_enabled: bool | None = None
    external_ai_enabled: bool | None = None

    @model_validator(mode="after")
    def external_ai_requires_ai(self):
        if self.external_ai_enabled is True and self.ai_assistance_enabled is False:
            raise ValueError("La IA externa no puede habilitarse si la asistencia IA está deshabilitada")
        return self


class OrganizationSettingsResponse(BaseModel):
    organization_id: str
    max_apk_size_mb: int = 100
    max_concurrent_analyses: int = 5
    analysis_timeout_seconds: int = 900
    retention_days: int = 90
    ai_assistance_enabled: bool = True
    external_ai_enabled: bool = False
    updated_at: datetime | None = None


class ToolPolicyUpdate(BaseModel):
    enabled_tools: list[str] = Field(min_length=1, max_length=3)

    @model_validator(mode="after")
    def unique_and_supported_tools(self):
        supported = {"jadx", "apktool", "mobsf"}
        if len(self.enabled_tools) != len(set(self.enabled_tools)):
            raise ValueError("No se permiten herramientas duplicadas")
        unknown = set(self.enabled_tools) - supported
        if unknown:
            raise ValueError(f"Herramientas no soportadas: {', '.join(sorted(unknown))}")
        return self


class ToolPolicyResponse(BaseModel):
    organization_id: str
    enabled_tools: list[str]
    available_tools: list[dict[str, str]]
    updated_at: datetime | None = None


class AdministrationAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    action: str
    resource_type: str
    resource_id: str | None
    result: str
    created_at: datetime
