from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_organization_member
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.application import APKVersion, Application
from app.models.finding import Finding
from app.models.identity import User
from app.schemas.dashboard import DashboardAnalysis, DashboardFinding, DashboardResponse, DashboardCounts

router = APIRouter(prefix="/organizations/{organization_id}/dashboard", tags=["dashboard"])

@router.get("", response_model=DashboardResponse)
def get_dashboard(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)

    app_count = db.scalar(select(func.count(Application.id)).where(Application.organization_id == organization_id)) or 0
    version_count = db.scalar(
        select(func.count(APKVersion.id)).join(Application).where(Application.organization_id == organization_id)
    ) or 0
    analysis_count = db.scalar(select(func.count(Analysis.id)).where(Analysis.organization_id == organization_id)) or 0
    finding_base = select(Finding.id).join(Analysis).where(Analysis.organization_id == organization_id)
    finding_count = db.scalar(select(func.count()).select_from(finding_base.subquery())) or 0
    pending = db.scalar(select(func.count(Finding.id)).join(Analysis).where(Analysis.organization_id == organization_id, Finding.review_state == "PENDING")) or 0
    critical = db.scalar(select(func.count(Finding.id)).join(Analysis).where(Analysis.organization_id == organization_id, Finding.severity == "CRITICAL")) or 0
    high = db.scalar(select(func.count(Finding.id)).join(Analysis).where(Analysis.organization_id == organization_id, Finding.severity == "HIGH")) or 0

    recent_stmt = (
        select(Analysis, Application.name, Application.package_name, APKVersion.version_name)
        .join(APKVersion, Analysis.apk_version_id == APKVersion.id)
        .join(Application, APKVersion.application_id == Application.id)
        .where(Analysis.organization_id == organization_id)
        .order_by(Analysis.created_at.desc())
        .limit(10)
    )
    analyses = []
    for analysis, app_name, package_name, version_name in db.execute(recent_stmt).all():
        count = db.scalar(select(func.count(Finding.id)).where(Finding.analysis_id == analysis.id)) or 0
        analyses.append(DashboardAnalysis(
            id=analysis.id, application_name=app_name, package_name=package_name,
            version_name=version_name, state=analysis.state, created_at=analysis.created_at,
            finished_at=analysis.finished_at, finding_count=count,
        ))

    finding_stmt = (
        select(Finding, Application.name)
        .join(Analysis, Finding.analysis_id == Analysis.id)
        .join(APKVersion, Analysis.apk_version_id == APKVersion.id)
        .join(Application, APKVersion.application_id == Application.id)
        .where(Analysis.organization_id == organization_id)
        .order_by(Finding.created_at.desc())
        .limit(10)
    )
    findings = [DashboardFinding(
        id=f.id, title=f.title, severity=f.severity, priority=f.priority,
        review_state=f.review_state, category=f.category, application_name=app_name,
        created_at=f.created_at,
    ) for f, app_name in db.execute(finding_stmt).all()]

    return DashboardResponse(
        counts=DashboardCounts(applications=app_count, versions=version_count, analyses=analysis_count,
                               findings=finding_count, pending_findings=pending,
                               critical_findings=critical, high_findings=high),
        analyses=analyses,
        findings=findings,
    )
