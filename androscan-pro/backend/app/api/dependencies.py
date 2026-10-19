from collections.abc import Generator
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.identity import Organization, Role, User, user_organization_roles

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticación requerida")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "access":
            raise ValueError
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido") from None

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no disponible")
    return user


def get_current_trace_id(request: Request) -> str:
    return request.headers.get("X-Trace-Id") or str(uuid4())


def get_organization_or_404(db: Session, organization_id: str) -> Organization:
    organization = db.get(Organization, organization_id)
    if not organization or not organization.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organización no encontrada")
    return organization


def get_user_roles(db: Session, user_id: str, organization_id: str) -> list[Role]:
    stmt = (
        select(Role)
        .join(user_organization_roles, Role.id == user_organization_roles.c.role_id)
        .where(
            user_organization_roles.c.user_id == user_id,
            user_organization_roles.c.organization_id == organization_id,
        )
    )
    return list(db.scalars(stmt).all())


def require_organization_member(organization_id: str, db: Session, current_user: User) -> Organization:
    organization = get_organization_or_404(db, organization_id)
    stmt = select(user_organization_roles.c.user_id).where(
        user_organization_roles.c.user_id == current_user.id,
        user_organization_roles.c.organization_id == organization_id,
    )
    if db.scalar(stmt) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso a la organización denegado")
    return organization


def require_role(*allowed_roles: str):
    def dependency(
        organization_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        require_organization_member(organization_id, db, current_user)
        roles = {role.name for role in get_user_roles(db, current_user.id, organization_id)}
        if not roles.intersection(allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
        return current_user

    return dependency
