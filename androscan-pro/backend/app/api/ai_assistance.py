from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, require_role, require_organization_member
from app.db.session import get_db
from app.models.ai_assistance import AIAssistance
from app.models.analysis import Analysis
from app.models.finding import Finding
from app.models.identity import User
from app.models.organization_configuration import OrganizationConfiguration
from app.schemas.ai_assistance import AIAssistanceCreate, AIAssistanceResponse
from app.services.ai_assistance import DISCLAIMER, draft_assistance
from app.services.audit import record_audit

router = APIRouter(prefix="/organizations/{organization_id}/analyses/{analysis_id}/ai-assistance", tags=["ai-assistance"])

@router.post("", response_model=AIAssistanceResponse, status_code=status.HTTP_201_CREATED)
def create_assistance(organization_id: str, analysis_id: str, payload: AIAssistanceCreate,
                      current_user: User = Depends(require_role("ADMIN", "ANALYST", "IT_MANAGER")),
                      db: Session = Depends(get_db)):
    org_config = db.scalar(select(OrganizationConfiguration).where(
        OrganizationConfiguration.organization_id == organization_id
    ))
    if org_config and not org_config.settings_json.get("ai_assistance_enabled", True):
        raise HTTPException(status_code=403, detail="La asistencia IA está deshabilitada para esta organización")
    analysis = db.scalar(select(Analysis).where(Analysis.id == analysis_id, Analysis.organization_id == organization_id))
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado en esta organización")
    stmt = select(Finding).where(Finding.analysis_id == analysis_id)
    if payload.finding_ids:
        stmt = stmt.where(Finding.id.in_(payload.finding_ids))
    findings = list(db.scalars(stmt.order_by(Finding.created_at.asc())).all())
    if payload.finding_ids and {f.id for f in findings} != set(payload.finding_ids):
        raise HTTPException(status_code=422, detail="Uno o más hallazgos no pertenecen al análisis indicado")
    result = draft_assistance(findings)
    item = AIAssistance(organization_id=organization_id, analysis_id=analysis_id,
        requested_by_user_id=current_user.id, provider="local-rule-assistant", status="REVIEW_REQUIRED",
        input_finding_ids=[f.id for f in findings], result_json=result, disclaimer=DISCLAIMER)
    db.add(item); db.flush()
    record_audit(db, actor_user_id=current_user.id, organization_id=organization_id,
        action="AI_ASSISTANCE_CREATED", resource_type="AI_ASSISTANCE", resource_id=item.id,
        result="SUCCESS", trace_id=analysis.trace_id)
    db.commit(); db.refresh(item)
    return item

@router.get("", response_model=list[AIAssistanceResponse])
def list_assistance(organization_id: str, analysis_id: str,
                    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_organization_member(organization_id, db, current_user)
    if not db.scalar(select(Analysis.id).where(Analysis.id == analysis_id, Analysis.organization_id == organization_id)):
        raise HTTPException(status_code=404, detail="Análisis no encontrado en esta organización")
    return list(db.scalars(select(AIAssistance).where(AIAssistance.organization_id == organization_id,
        AIAssistance.analysis_id == analysis_id).order_by(AIAssistance.created_at.desc())).all())
