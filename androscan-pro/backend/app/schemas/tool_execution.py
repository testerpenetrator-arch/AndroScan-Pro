from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ToolExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    tool_id: str
    tool_name: str
    tool_version: str
    state: str
    exit_code: int | None
    stdout: str
    stderr: str
    started_at: datetime
    finished_at: datetime
    created_at: datetime
