from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_user_roles, require_organization_member, require_role
from app.core.security import hash_password
from app.db.session import get_db
from app.models.identity import Organization, Role, User, user_organization_roles
from app.schemas.identity import (
    AssignRolesRequest,
    OrganizationCreate,
    OrganizationResponse,
    RoleResponse,
    UserCreate,
    UserResponse,
    UserWithRolesResponse,
)
from app.services.audit import record_audit

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[OrganizationResponse])
def list_organizations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Organization).join(user_organization_roles, Organization.id == user_organization_roles.c.organization_id).where(
        user_organization_roles.c.user_id == current_user.id,
        Organization.is_active.is_(True),
    )
    return list(db.scalars(stmt).unique().all())


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.scalar(select(Organization).where(Organization.slug == payload.slug)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El slug ya existe")
    organization = Organization(name=payload.name, slug=payload.slug)
    db.add(organization)
    db.flush()
    admin_role = db.scalar(select(Role).where(Role.name == "ADMIN"))
    if not admin_role:
        raise HTTPException(status_code=500, detail="Roles base no inicializados")
    db.execute(
        user_organization_roles.insert().values(
            user_id=current_user.id, organization_id=organization.id, role_id=admin_role.id
        )
    )
    record_audit(
        db,
        actor_user_id=current_user.id,
        organization_id=organization.id,
        action="ORGANIZATION_CREATE",
        resource_type="ORGANIZATION",
        resource_id=organization.id,
        result="SUCCESS",
        trace_id=None,
    )
    db.commit()
    db.refresh(organization)
    return organization


@router.get("/{organization_id}/users", response_model=list[UserResponse])
def list_users(
    organization_id: str,
    current_user: User = Depends(require_role("ADMIN", "IT_MANAGER")),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    stmt = select(User).join(user_organization_roles, User.id == user_organization_roles.c.user_id).where(
        user_organization_roles.c.organization_id == organization_id
    )
    return list(db.scalars(stmt).unique().all())


@router.post("/{organization_id}/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    organization_id: str,
    payload: UserCreate,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    if db.scalar(select(User).where(User.email == str(payload.email).lower())):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya existe")
    organization = require_organization_member(organization_id, db, current_user)
    user = User(email=str(payload.email).lower(), full_name=payload.full_name, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    default_role = db.scalar(select(Role).where(Role.name == "ANALYST"))
    if not default_role:
        raise HTTPException(status_code=500, detail="Roles base no inicializados")
    db.execute(user_organization_roles.insert().values(user_id=user.id, organization_id=organization.id, role_id=default_role.id))
    record_audit(
        db,
        actor_user_id=current_user.id,
        organization_id=organization_id,
        action="USER_CREATE",
        resource_type="USER",
        resource_id=user.id,
        result="SUCCESS",
        trace_id=None,
    )
    db.commit()
    db.refresh(user)
    return user


@router.get("/{organization_id}/users/{user_id}/roles", response_model=list[RoleResponse])
def get_roles(
    organization_id: str,
    user_id: str,
    current_user: User = Depends(require_role("ADMIN", "IT_MANAGER")),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return get_user_roles(db, user_id, organization_id)


@router.put("/{organization_id}/users/{user_id}/roles", response_model=list[RoleResponse])
def assign_roles(
    organization_id: str,
    user_id: str,
    payload: AssignRolesRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    require_organization_member(organization_id, db, current_user)
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    roles = list(db.scalars(select(Role).where(Role.name.in_(payload.role_names))).all())
    if len(roles) != len(set(payload.role_names)):
        raise HTTPException(status_code=422, detail="Uno o más roles no existen")

    db.execute(
        user_organization_roles.delete().where(
            user_organization_roles.c.user_id == user_id,
            user_organization_roles.c.organization_id == organization_id,
        )
    )
    for role in roles:
        db.execute(
            user_organization_roles.insert().values(
                user_id=user_id, organization_id=organization_id, role_id=role.id
            )
        )
    record_audit(
        db,
        actor_user_id=current_user.id,
        organization_id=organization_id,
        action="USER_ROLES_UPDATE",
        resource_type="USER",
        resource_id=user_id,
        result="SUCCESS",
        trace_id=None,
    )
    db.commit()
    return roles
