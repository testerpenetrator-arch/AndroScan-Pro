from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class AIAssistanceCreate(BaseModel):
    finding_ids: list[str] = Field(default_factory=list, max_length=100)

class AIAssistanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    organization_id: str
    analysis_id: str
    requested_by_user_id: str | None
    provider: str
    status: str
    input_finding_ids: list
    result_json: dict
    disclaimer: str
    created_at: datetime
