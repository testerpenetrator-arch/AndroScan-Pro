from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisCreate(BaseModel):
    trace_id: str | None = Field(default=None, min_length=1, max_length=64)


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    apk_version_id: str
    state: str
    requested_by_user_id: str | None
    trace_id: str | None
    attempt: int
    queued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    error_code: str | None
    error_message: str | None
    summary_json: dict
    created_at: datetime
    updated_at: datetime
