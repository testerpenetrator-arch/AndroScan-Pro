from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    package_name: str = Field(min_length=1, max_length=255, pattern=r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$")


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    name: str
    package_name: str
    created_at: datetime


class APKVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    original_filename: str
    size_bytes: int
    sha256: str
    mime_type: str
    version_name: str | None
    version_code: str | None
    metadata_json: dict
    validation_status: str
    created_at: datetime
