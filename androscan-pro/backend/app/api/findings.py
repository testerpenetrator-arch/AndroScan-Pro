from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, require_organization_member, require_role
from app.db.session import get_db
from app.models.identity import User
from app.models.analysis import Analysis
from app.models.tool_execution import ToolExecution
from app.models.finding import Finding, FindingReview
from app.schemas.finding import FindingCreate, FindingResponse, FindingReviewCreate, FindingReviewResponse
from app.services.audit import record_audit

router = APIRouter(prefix="/organizations/{organization_id}/analyses/{analysis_id}/findings", tags=["findings"])

def _analysis(db, org, aid):
    return db.scalar(select(Analysis).where(Analysis.id==aid, Analysis.organization_id==org))

@router.get("", response_model=list[FindingResponse])
def list_findings(organization_id: str, analysis_id: str, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    require_organization_member(organization_id, db, current_user)
    if not _analysis(db, organization_id, analysis_id): raise HTTPException(404,"Análisis no encontrado")
    return list(db.scalars(select(Finding).where(Finding.analysis_id==analysis_id).order_by(Finding.created_at.asc())).all())

@router.post("", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
def create_finding(organization_id: str, analysis_id: str, payload: FindingCreate, current_user: User=Depends(require_role("ADMIN","ANALYST")), db: Session=Depends(get_db)):
    analysis=_analysis(db,organization_id,analysis_id)
    if not analysis: raise HTTPException(404,"Análisis no encontrado")
    te=db.scalar(select(ToolExecution).where(ToolExecution.id==payload.tool_execution_id, ToolExecution.analysis_id==analysis_id))
    if not te: raise HTTPException(422,"La ejecución de herramienta no pertenece al análisis")
    f=Finding(analysis_id=analysis_id,tool_execution_id=te.id,rule_id=payload.rule_id,correlation_key=payload.correlation_key,title=payload.title,description=payload.description,category=payload.category,severity=payload.severity,priority=payload.priority,evidence_json=payload.evidence,raw_result_ref=payload.raw_result_ref)
    db.add(f); db.flush()
    record_audit(db,actor_user_id=current_user.id,organization_id=organization_id,action="FINDING_CREATED",resource_type="FINDING",resource_id=f.id,result="SUCCESS")
    db.commit(); db.refresh(f); return f

@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(organization_id: str, analysis_id: str, finding_id: str, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    require_organization_member(organization_id,db,current_user)
    if not _analysis(db,organization_id,analysis_id): raise HTTPException(404,"Análisis no encontrado")
    f=db.scalar(select(Finding).where(Finding.id==finding_id,Finding.analysis_id==analysis_id))
    if not f: raise HTTPException(404,"Hallazgo no encontrado")
    return f

@router.post("/{finding_id}/reviews", response_model=FindingReviewResponse, status_code=status.HTTP_201_CREATED)
def review_finding(organization_id: str, analysis_id: str, finding_id: str, payload: FindingReviewCreate, current_user: User=Depends(require_role("ADMIN","ANALYST")), db: Session=Depends(get_db)):
    if not _analysis(db,organization_id,analysis_id): raise HTTPException(404,"Análisis no encontrado")
    f=db.scalar(select(Finding).where(Finding.id==finding_id,Finding.analysis_id==analysis_id))
    if not f: raise HTTPException(404,"Hallazgo no encontrado")
    f.review_state=payload.state; f.analyst_notes=payload.justification
    review=FindingReview(finding_id=f.id,analyst_user_id=current_user.id,state=payload.state,justification=payload.justification)
    db.add(review)
    record_audit(db,actor_user_id=current_user.id,organization_id=organization_id,action="FINDING_REVIEWED",resource_type="FINDING",resource_id=f.id,result="SUCCESS")
    db.commit(); db.refresh(review); return review

@router.get("/{finding_id}/reviews", response_model=list[FindingReviewResponse])
def list_reviews(organization_id: str, analysis_id: str, finding_id: str, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    require_organization_member(organization_id,db,current_user)
    if not db.scalar(select(Finding.id).where(Finding.id==finding_id,Finding.analysis_id==analysis_id)): raise HTTPException(404,"Hallazgo no encontrado")
    return list(db.scalars(select(FindingReview).where(FindingReview.finding_id==finding_id).order_by(FindingReview.created_at.asc())).all())
