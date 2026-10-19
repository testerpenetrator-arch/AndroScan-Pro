from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.session import get_db
from app.models.audit import AuditEvent
from app.models.identity import User
from app.models.organization_configuration import OrganizationConfiguration
from app.schemas.administration import (
    OrganizationSettingsResponse, OrganizationSettingsUpdate,
    ToolPolicyResponse, ToolPolicyUpdate,
)
from app.services.audit import record_audit
from app.services.tools.registry import TOOL_REGISTRY

router = APIRouter(prefix="/organizations/{organization_id}/admin", tags=["administration"])
DEFAULT_SETTINGS = {
    "max_apk_size_mb": 100,
    "max_concurrent_analyses": 5,
    "analysis_timeout_seconds": 900,
    "retention_days": 90,
    "ai_assistance_enabled": True,
    "external_ai_enabled": False,
}
DEFAULT_ENABLED_TOOLS = ["jadx", "apktool", "mobsf"]


def _get_or_create(db: Session, organization_id: str) -> OrganizationConfiguration:
    row = db.scalar(select(OrganizationConfiguration).where(
        OrganizationConfiguration.organization_id == organization_id
    ))
    if row:
        return row
    row = OrganizationConfiguration(
        organization_id=organization_id,
        settings_json=DEFAULT_SETTINGS.copy(),
        tool_policy_json={"enabled_tools": DEFAULT_ENABLED_TOOLS.copy()},
    )
    db.add(row)
    db.flush()
    return row


@router.get("/settings", response_model=OrganizationSettingsResponse)
def get_settings(organization_id: str, current_user: User = Depends(require_role("ADMIN", "IT_MANAGER")), db: Session = Depends(get_db)):
    row = _get_or_create(db, organization_id)
    db.commit()
    return OrganizationSettingsResponse(organization_id=organization_id, **{**DEFAULT_SETTINGS, **row.settings_json}, updated_at=row.updated_at)


@router.put("/settings", response_model=OrganizationSettingsResponse)
def update_settings(organization_id: str, payload: OrganizationSettingsUpdate,
                    current_user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    row = _get_or_create(db, organization_id)
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    updated = {**DEFAULT_SETTINGS, **row.settings_json, **updates}
    if updated.get("external_ai_enabled") and not updated.get("ai_assistance_enabled"):
        raise HTTPException(status_code=422, detail="La IA externa requiere que la asistencia IA esté habilitada")
    row.settings_json = updated
    row.updated_by_user_id = current_user.id
    record_audit(db, actor_user_id=current_user.id, organization_id=organization_id,
        action="ORGANIZATION_SETTINGS_UPDATE", resource_type="ORGANIZATION_CONFIGURATION",
        resource_id=row.id, result="SUCCESS", trace_id=None)
    db.commit(); db.refresh(row)
    return OrganizationSettingsResponse(organization_id=organization_id, **updated, updated_at=row.updated_at)


@router.get("/tools", response_model=ToolPolicyResponse)
def get_tool_policy(organization_id: str, current_user: User = Depends(require_role("ADMIN", "IT_MANAGER")), db: Session = Depends(get_db)):
    row = _get_or_create(db, organization_id)
    db.commit()
    return ToolPolicyResponse(organization_id=organization_id,
        enabled_tools=row.tool_policy_json.get("enabled_tools", DEFAULT_ENABLED_TOOLS),
        available_tools=[{"id": t.tool_id, "name": t.name, "version": t.version} for t in TOOL_REGISTRY],
        updated_at=row.updated_at)


@router.put("/tools", response_model=ToolPolicyResponse)
def update_tool_policy(organization_id: str, payload: ToolPolicyUpdate,
                       current_user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    row = _get_or_create(db, organization_id)
    row.tool_policy_json = {"enabled_tools": payload.enabled_tools}
    row.updated_by_user_id = current_user.id
    record_audit(db, actor_user_id=current_user.id, organization_id=organization_id,
        action="ORGANIZATION_TOOL_POLICY_UPDATE", resource_type="ORGANIZATION_CONFIGURATION",
        resource_id=row.id, result="SUCCESS", trace_id=None)
    db.commit(); db.refresh(row)
    return ToolPolicyResponse(organization_id=organization_id, enabled_tools=payload.enabled_tools,
        available_tools=[{"id": t.tool_id, "name": t.name, "version": t.version} for t in TOOL_REGISTRY],
        updated_at=row.updated_at)


@router.get("/audit", response_model=list[dict])
def list_admin_audit(organization_id: str, limit: int = 50,
                     current_user: User = Depends(require_role("ADMIN", "IT_MANAGER")), db: Session = Depends(get_db)):
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=422, detail="limit debe estar entre 1 y 200")
    events = db.scalars(select(AuditEvent).where(AuditEvent.organization_id == organization_id)
        .order_by(AuditEvent.created_at.desc()).limit(limit)).all()
    return [{"id": e.id, "action": e.action, "resource_type": e.resource_type,
             "resource_id": e.resource_id, "result": e.result, "created_at": e.created_at}
            for e in events]
