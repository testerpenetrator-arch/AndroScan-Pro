from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.finding import CATEGORIES, SEVERITIES, PRIORITIES, REVIEW_STATES

class FindingCreate(BaseModel):
    tool_execution_id: str
    rule_id: str | None = None
    correlation_key: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    category: str
    severity: str
    priority: str = "P3"
    evidence: dict = Field(default_factory=dict)
    raw_result_ref: str | None = None
    @field_validator("category")
    @classmethod
    def category_valid(cls,v):
        if v not in CATEGORIES: raise ValueError("Categoría no válida")
        return v
    @field_validator("severity")
    @classmethod
    def severity_valid(cls,v):
        if v not in SEVERITIES: raise ValueError("Severidad no válida")
        return v
    @field_validator("priority")
    @classmethod
    def priority_valid(cls,v):
        if v not in PRIORITIES: raise ValueError("Prioridad no válida")
        return v

class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; analysis_id: str; tool_execution_id: str; rule_id: str | None
    correlation_key: str; title: str; description: str; category: str; severity: str; priority: str
    evidence_json: dict; raw_result_ref: str | None; review_state: str; analyst_notes: str | None
    created_at: datetime; updated_at: datetime

class FindingReviewCreate(BaseModel):
    state: str
    justification: str = Field(min_length=1, max_length=4000)
    @field_validator("state")
    @classmethod
    def state_valid(cls,v):
        if v not in {"CONFIRMED","DISMISSED"}: raise ValueError("Estado de revisión no válido")
        return v

class FindingReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; finding_id: str; analyst_user_id: str; state: str; justification: str; created_at: datetime
