from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_organization_member
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.application import APKVersion
from app.models.finding import Finding
from app.models.identity import User
from app.schemas.comparison import ComparisonCreate, ComparisonResponse, FindingDelta

router = APIRouter(prefix="/organizations/{organization_id}/comparisons", tags=["comparisons"])


def _finding_snapshot(f: Finding) -> dict:
    return {
        "id": f.id,
        "title": f.title,
        "description": f.description,
        "category": f.category,
        "severity": f.severity,
        "priority": f.priority,
        "review_state": f.review_state,
    }


@router.post("", response_model=ComparisonResponse)
def compare_analyses(
    organization_id: str,
    payload: ComparisonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    a = db.scalar(select(Analysis).where(Analysis.id == payload.analysis_a_id, Analysis.organization_id == organization_id))
    b = db.scalar(select(Analysis).where(Analysis.id == payload.analysis_b_id, Analysis.organization_id == organization_id))
    if not a or not b:
        raise HTTPException(status_code=404, detail="Uno o ambos análisis no existen en esta organización")
    va = db.get(APKVersion, a.apk_version_id)
    vb = db.get(APKVersion, b.apk_version_id)
    if not va or not vb or va.application_id != vb.application_id:
        raise HTTPException(status_code=422, detail="Los análisis deben pertenecer a la misma aplicación")
    if a.id == b.id:
        raise HTTPException(status_code=422, detail="Seleccione dos análisis diferentes")

    before = list(db.scalars(select(Finding).where(Finding.analysis_id == a.id).order_by(Finding.created_at.asc())).all())
    after = list(db.scalars(select(Finding).where(Finding.analysis_id == b.id).order_by(Finding.created_at.asc())).all())
    # Match one-to-one by correlation_key so duplicate findings retain their individual provenance.
    buckets_a: dict[str, list[Finding]] = {}
    buckets_b: dict[str, list[Finding]] = {}
    for f in before:
        buckets_a.setdefault(f.correlation_key, []).append(f)
    for f in after:
        buckets_b.setdefault(f.correlation_key, []).append(f)
    deltas: list[FindingDelta] = []
    counts = {"ADDED": 0, "REMOVED": 0, "UNCHANGED": 0, "CHANGED": 0}
    for key in sorted(set(buckets_a) | set(buckets_b)):
        left, right = list(buckets_a.get(key, [])), list(buckets_b.get(key, []))
        while left and right:
            old, new = left.pop(0), right.pop(0)
            old_s, new_s = _finding_snapshot(old), _finding_snapshot(new)
            comparable = ("title", "description", "category", "severity", "priority")
            state = "UNCHANGED" if all(old_s[k] == new_s[k] for k in comparable) else "CHANGED"
            counts[state] += 1
            deltas.append(FindingDelta(correlation_key=key, status=state, before=old_s, after=new_s))
        for old in left:
            counts["REMOVED"] += 1
            deltas.append(FindingDelta(correlation_key=key, status="REMOVED", before=_finding_snapshot(old), after=None))
        for new in right:
            counts["ADDED"] += 1
            deltas.append(FindingDelta(correlation_key=key, status="ADDED", before=None, after=_finding_snapshot(new)))
    return ComparisonResponse(
        analysis_a_id=a.id,
        analysis_b_id=b.id,
        application_id=va.application_id,
        summary=counts,
        findings=deltas,
    )
