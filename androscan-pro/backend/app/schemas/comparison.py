from pydantic import BaseModel, Field

class ComparisonCreate(BaseModel):
    analysis_a_id: str = Field(min_length=1, max_length=36)
    analysis_b_id: str = Field(min_length=1, max_length=36)

class FindingDelta(BaseModel):
    correlation_key: str
    status: str
    before: dict | None = None
    after: dict | None = None

class ComparisonResponse(BaseModel):
    analysis_a_id: str
    analysis_b_id: str
    application_id: str
    summary: dict[str, int]
    findings: list[FindingDelta]
