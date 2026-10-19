from __future__ import annotations

from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_organization_member
from app.core.config import get_settings
from app.db.session import get_db
from app.models.application import APKVersion, Application
from app.models.identity import User
from app.models.organization_configuration import OrganizationConfiguration
from app.schemas.application import APKVersionResponse, ApplicationCreate, ApplicationResponse
from app.services.apk_storage import ObjectStorageError, S3ObjectStorage
from app.services.apk_validation import APKValidationError, validate_apk, validate_package_name
from app.services.audit import record_audit

router = APIRouter(prefix="/organizations/{organization_id}/applications", tags=["applications"])


def _get_application_or_404(db: Session, organization_id: str, application_id: str) -> Application:
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.organization_id == organization_id,
        )
    )
    if not application:
        raise HTTPException(status_code=404, detail="Aplicación no encontrada")
    return application


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    organization_id: str,
    payload: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    try:
        validate_package_name(payload.package_name)
    except APKValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    exists = db.scalar(
        select(Application).where(
            Application.organization_id == organization_id,
            Application.package_name == payload.package_name,
        )
    )
    if exists:
        raise HTTPException(status_code=409, detail="Ya existe una aplicación con ese package_name en la organización")

    application = Application(
        organization_id=organization_id,
        name=payload.name,
        package_name=payload.package_name,
    )
    db.add(application)
    db.flush()
    record_audit(
        db,
        actor_user_id=current_user.id,
        organization_id=organization_id,
        action="APPLICATION_CREATE",
        resource_type="APPLICATION",
        resource_id=application.id,
        result="SUCCESS",
        trace_id=None,
    )
    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    stmt = select(Application).where(Application.organization_id == organization_id).order_by(Application.created_at.desc())
    return list(db.scalars(stmt).all())


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    organization_id: str,
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    return _get_application_or_404(db, organization_id, application_id)


@router.get("/{application_id}/versions", response_model=list[APKVersionResponse])
def list_versions(
    organization_id: str,
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    application = _get_application_or_404(db, organization_id, application_id)
    stmt = select(APKVersion).where(APKVersion.application_id == application.id).order_by(APKVersion.created_at.desc())
    return list(db.scalars(stmt).all())


@router.post("/{application_id}/apk", response_model=APKVersionResponse, status_code=status.HTTP_201_CREATED)
async def upload_apk(
    organization_id: str,
    application_id: str,
    file: UploadFile = File(...),
    version_name: str | None = Form(default=None),
    version_code: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    application = _get_application_or_404(db, organization_id, application_id)
    settings = get_settings()
    org_config = db.scalar(select(OrganizationConfiguration).where(
        OrganizationConfiguration.organization_id == organization_id
    ))
    configured_max_mb = (org_config.settings_json.get("max_apk_size_mb", settings.max_apk_size_mb)
                         if org_config else settings.max_apk_size_mb)

    try:
        validation = await validate_apk(file, configured_max_mb * 1024 * 1024)
    except APKValidationError as exc:
        record_audit(
            db,
            actor_user_id=current_user.id,
            organization_id=organization_id,
            action="APK_UPLOAD_REJECT",
            resource_type="APPLICATION",
            resource_id=application.id,
            result="REJECTED",
            trace_id=None,
        )
        db.commit()
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    duplicate = db.scalar(
        select(APKVersion).where(
            APKVersion.application_id == application.id,
            APKVersion.sha256 == validation.sha256,
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="El APK ya fue registrado para esta aplicación")

    safe_filename = PurePosixPath((file.filename or "upload.apk").replace("\\", "/")).name
    storage_key = f"organizations/{organization_id}/applications/{application.id}/versions/{validation.sha256}/{safe_filename}"
    await file.seek(0)
    try:
        S3ObjectStorage().put_fileobj(
            storage_key,
            file.file,
            content_type=file.content_type or "application/vnd.android.package-archive",
            content_length=validation.size_bytes,
        )
    except ObjectStorageError as exc:
        record_audit(
            db,
            actor_user_id=current_user.id,
            organization_id=organization_id,
            action="APK_STORAGE_FAILURE",
            resource_type="APPLICATION",
            resource_id=application.id,
            result="ERROR",
            trace_id=None,
        )
        db.commit()
        raise HTTPException(status_code=503, detail="No fue posible almacenar el APK") from exc

    version = APKVersion(
        application_id=application.id,
        original_filename=file.filename,
        size_bytes=validation.size_bytes,
        sha256=validation.sha256,
        mime_type=file.content_type or "application/vnd.android.package-archive",
        storage_key=storage_key,
        version_name=version_name,
        version_code=version_code,
        metadata_json=validation.metadata,
        validation_status="VALIDATED",
    )
    db.add(version)
    db.flush()
    record_audit(
        db,
        actor_user_id=current_user.id,
        organization_id=organization_id,
        action="APK_UPLOAD_ACCEPT",
        resource_type="APK_VERSION",
        resource_id=version.id,
        result="SUCCESS",
        trace_id=None,
    )
    db.commit()
    db.refresh(version)
    return version
