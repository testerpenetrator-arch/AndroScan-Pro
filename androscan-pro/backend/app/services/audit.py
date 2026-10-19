from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


def record_audit(
    db: Session,
    *,
    actor_user_id: str | None,
    organization_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None,
    result: str,
    trace_id: str | None,
) -> None:
    db.add(
        AuditEvent(
            actor_user_id=actor_user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            trace_id=trace_id,
        )
    )
