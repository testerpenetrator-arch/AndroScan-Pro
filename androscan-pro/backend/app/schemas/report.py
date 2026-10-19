from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class ReportCreate(BaseModel):
    analysis_id: str = Field(min_length=1, max_length=36)
    format: Literal["JSON", "HTML", "PDF"] = "JSON"

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    organization_id: str
    analysis_id: str
    requested_by_user_id: str | None
    format: str
    status: str
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    created_at: datetime
