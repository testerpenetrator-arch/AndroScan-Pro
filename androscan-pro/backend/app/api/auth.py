from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.identity import User
from app.schemas.identity import LoginRequest, TokenResponse
from app.services.audit import record_audit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = create_access_token(user.id)
    record_audit(
        db,
        actor_user_id=user.id,
        organization_id=None,
        action="AUTH_LOGIN",
        resource_type="USER",
        resource_id=user.id,
        result="SUCCESS",
        trace_id=None,
    )
    db.commit()
    return TokenResponse(access_token=token)
