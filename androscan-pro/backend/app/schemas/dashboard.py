from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DashboardCounts(BaseModel):
    applications: int
    versions: int
    analyses: int
    findings: int
    pending_findings: int
    critical_findings: int
    high_findings: int

class DashboardAnalysis(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    application_name: str
    package_name: str
    version_name: str | None
    state: str
    created_at: datetime
    finished_at: datetime | None
    finding_count: int

class DashboardFinding(BaseModel):
    id: str
    title: str
    severity: str
    priority: str
    review_state: str
    category: str
    application_name: str
    created_at: datetime

class DashboardResponse(BaseModel):
    counts: DashboardCounts
    analyses: list[DashboardAnalysis]
    findings: list[DashboardFinding]
