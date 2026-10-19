from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, require_organization_member, require_role
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.application import APKVersion, Application
from app.models.finding import Finding
from app.models.identity import User
from app.models.report import Report
from app.models.tool_execution import ToolExecution
from app.schemas.report import ReportCreate, ReportResponse
from app.services.audit import record_audit
from app.services.reporting import build_report_data, render_report, sha256_bytes

router = APIRouter(prefix="/organizations/{organization_id}/reports", tags=["reports"])

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(organization_id: str, payload: ReportCreate, current_user: User = Depends(require_role("ADMIN", "ANALYST", "IT_MANAGER")), db: Session = Depends(get_db)):
    analysis = db.scalar(select(Analysis).where(Analysis.id == payload.analysis_id, Analysis.organization_id == organization_id))
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado en esta organización")
    version = db.get(APKVersion, analysis.apk_version_id)
    application = db.get(Application, version.application_id) if version else None
    if not version or not application or application.organization_id != organization_id:
        raise HTTPException(status_code=404, detail="Versión APK no encontrada")
    findings = list(db.scalars(select(Finding).where(Finding.analysis_id == analysis.id).order_by(Finding.created_at.asc())).all())
    tools = list(db.scalars(select(ToolExecution).where(ToolExecution.analysis_id == analysis.id).order_by(ToolExecution.created_at.asc())).all())
    data = build_report_data(organization_id, analysis, version, application, findings, tools)
    content_type, extension, content = render_report(data, payload.format)
    report = Report(organization_id=organization_id, analysis_id=analysis.id, requested_by_user_id=current_user.id, format=payload.format, status="COMPLETED", filename=f"androscan-{analysis.id}.{extension}", content_type=content_type, content=content.decode("latin1") if payload.format == "PDF" else content.decode("utf-8"), size_bytes=len(content), sha256=sha256_bytes(content))
    # Latin-1 round-trip preserves arbitrary PDF bytes in the text column without lossy conversion.
    db.add(report); db.flush()
    record_audit(db, actor_user_id=current_user.id, organization_id=organization_id, action="REPORT_CREATED", resource_type="REPORT", resource_id=report.id, result="SUCCESS", trace_id=analysis.trace_id)
    db.commit(); db.refresh(report)
    return report

@router.get("", response_model=list[ReportResponse])
def list_reports(organization_id: str, analysis_id: str | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_organization_member(organization_id, db, current_user)
    stmt = select(Report).where(Report.organization_id == organization_id)
    if analysis_id:
        if not db.scalar(select(Analysis.id).where(Analysis.id == analysis_id, Analysis.organization_id == organization_id)):
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        stmt = stmt.where(Report.analysis_id == analysis_id)
    return list(db.scalars(stmt.order_by(Report.created_at.desc())).all())

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(organization_id: str, report_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_organization_member(organization_id, db, current_user)
    report = db.scalar(select(Report).where(Report.id == report_id, Report.organization_id == organization_id))
    if not report: raise HTTPException(status_code=404, detail="Informe no encontrado")
    return report

@router.get("/{report_id}/download")
def download_report(organization_id: str, report_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_organization_member(organization_id, db, current_user)
    report = db.scalar(select(Report).where(Report.id == report_id, Report.organization_id == organization_id))
    if not report: raise HTTPException(status_code=404, detail="Informe no encontrado")
    raw = report.content.encode("latin1") if report.format == "PDF" else report.content.encode("utf-8")
    if sha256_bytes(raw) != report.sha256:
        raise HTTPException(status_code=500, detail="La integridad del informe almacenado no coincide")
    return Response(content=raw, media_type=report.content_type, headers={"Content-Disposition": f'attachment; filename="{report.filename}"', "X-Content-SHA256": report.sha256})
