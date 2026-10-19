from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_organization_member
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.application import APKVersion, Application
from app.models.identity import User
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.schemas.tool_execution import ToolExecutionResponse
from app.models.tool_execution import ToolExecution
from app.services.analysis_orchestrator import get_analysis_for_org, transition_analysis
from app.services.analysis_tasks import queue_analysis_task
from app.services.audit import record_audit
from app.services.sandbox import DockerSandboxManager, SandboxError

router = APIRouter(prefix="/organizations/{organization_id}", tags=["analyses"])


def _get_version_for_org(db: Session, organization_id: str, version_id: str) -> APKVersion | None:
    return db.scalar(
        select(APKVersion)
        .join(Application, APKVersion.application_id == Application.id)
        .where(APKVersion.id == version_id, Application.organization_id == organization_id)
    )


@router.post("/versions/{version_id}/analyses", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
def create_analysis(
    organization_id: str,
    version_id: str,
    payload: AnalysisCreate | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    version = _get_version_for_org(db, organization_id, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Versión APK no encontrada")
    if version.validation_status != "VALIDATED":
        raise HTTPException(status_code=409, detail="La versión APK no está validada")

    analysis = Analysis(
        organization_id=organization_id,
        apk_version_id=version.id,
        requested_by_user_id=current_user.id,
        trace_id=(payload.trace_id if payload else None),
        state="CREATED",
    )
    db.add(analysis)
    db.flush()
    transition_analysis(db, analysis, "QUEUED")
    record_audit(
        db,
        actor_user_id=current_user.id,
        organization_id=organization_id,
        action="ANALYSIS_QUEUED",
        resource_type="ANALYSIS",
        resource_id=analysis.id,
        result="SUCCESS",
        trace_id=analysis.trace_id,
    )
    db.commit()
    db.refresh(analysis)

    try:
        queue_analysis_task.delay(analysis.id)
    except Exception as exc:
        db.rollback()
        # La cola es necesaria para el modelo asíncrono; no se oculta el fallo.
        raise HTTPException(status_code=503, detail="No fue posible encolar el análisis") from exc

    return analysis


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    organization_id: str,
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    analysis = get_analysis_for_org(db, organization_id, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return analysis


@router.get("/applications/{application_id}/analyses", response_model=list[AnalysisResponse])
def list_application_analyses(
    organization_id: str,
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.organization_id == organization_id,
        )
    )
    if not application:
        raise HTTPException(status_code=404, detail="Aplicación no encontrada")

    stmt = (
        select(Analysis)
        .join(APKVersion, Analysis.apk_version_id == APKVersion.id)
        .where(Analysis.organization_id == organization_id, APKVersion.application_id == application_id)
        .order_by(Analysis.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.get("/analyses/{analysis_id}/tools", response_model=list[ToolExecutionResponse])
def list_tool_executions(
    organization_id: str,
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    analysis = get_analysis_for_org(db, organization_id, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    stmt = select(ToolExecution).where(ToolExecution.analysis_id == analysis_id).order_by(ToolExecution.created_at.asc())
    return list(db.scalars(stmt).all())


@router.post("/analyses/{analysis_id}/cancel", response_model=AnalysisResponse)
def cancel_analysis(
    organization_id: str,
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    analysis = get_analysis_for_org(db, organization_id, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    if analysis.state in {"COMPLETED", "FAILED", "CANCELLED"}:
        raise HTTPException(status_code=409, detail="El análisis ya está en un estado final")

    try:
        transition_analysis(db, analysis, "CANCELLED")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if analysis.sandbox_container_id:
        try:
            DockerSandboxManager().remove(analysis.sandbox_container_id)
            analysis.sandbox_status = "REMOVED"
            analysis.sandbox_container_id = None
        except SandboxError:
            analysis.sandbox_status = "CLEANUP_FAILED"
    record_audit(
        db,
        actor_user_id=current_user.id,
        organization_id=organization_id,
        action="ANALYSIS_CANCEL",
        resource_type="ANALYSIS",
        resource_id=analysis.id,
        result="SUCCESS",
        trace_id=analysis.trace_id,
    )
    db.commit()
    db.refresh(analysis)
    return analysis
