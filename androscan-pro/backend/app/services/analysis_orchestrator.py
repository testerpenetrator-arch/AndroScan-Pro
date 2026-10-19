from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis import ANALYSIS_STATES, Analysis


TRANSITIONS: dict[str, set[str]] = {
    "CREATED": {"QUEUED", "CANCELLED"},
    "QUEUED": {"PREPARING", "CANCELLED", "FAILED"},
    "PREPARING": {"RUNNING", "CANCELLED", "FAILED"},
    "RUNNING": {"PROCESSING_RESULTS", "CANCELLED", "FAILED"},
    "PROCESSING_RESULTS": {"COMPLETED", "FAILED", "CANCELLED"},
    "COMPLETED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def transition_analysis(db: Session, analysis: Analysis, target: str) -> Analysis:
    if target not in ANALYSIS_STATES:
        raise ValueError(f"Estado de análisis no soportado: {target}")
    if target not in TRANSITIONS.get(analysis.state, set()):
        raise ValueError(f"Transición no permitida: {analysis.state} -> {target}")

    now = utc_now()
    analysis.state = target
    analysis.updated_at = now
    if target == "QUEUED":
        analysis.queued_at = now
    elif target == "RUNNING":
        analysis.started_at = now
    elif target in {"COMPLETED", "FAILED", "CANCELLED"}:
        analysis.finished_at = now
    db.flush()
    return analysis


def get_analysis_for_org(db: Session, organization_id: str, analysis_id: str) -> Analysis | None:
    return db.scalar(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.organization_id == organization_id,
        )
    )
