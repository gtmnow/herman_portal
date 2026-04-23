from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.auth_user import AuthUser
from app.schemas.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginRequest,
    LoginResponse,
    PortalUserSummary,
)
from app.services.credential_compat import load_credentials, record_failed_login, record_successful_login, set_password


class AuthService:
    def login(self, payload: LoginRequest, *, db: Session) -> LoginResponse:
        user = self._get_user_by_email(db, payload.email)
        credentials = load_credentials(db, user.user_id_hash) if user is not None else None
        if user is None or credentials is None or not verify_password(payload.password, credentials.password_hash):
            if user is not None and credentials is not None:
                record_failed_login(db, credentials)
                db.commit()
            raise ValueError("Invalid credentials.")
        if not user.is_active:
            raise PermissionError("User account is inactive.")
        if credentials.locked_until is not None and credentials.locked_until > datetime.utcnow():
            raise PermissionError("User account is temporarily locked.")

        now = datetime.utcnow()
        user.last_login_at = now
        record_successful_login(db, credentials, now)
        db.add(user)
        db.commit()

        return LoginResponse(
            user=PortalUserSummary(
                email=user.email,
                user_id_hash=user.user_id_hash,
                display_name=user.display_name,
                tenant_id=user.tenant_id,
            ),
        )

    def change_password(self, payload: ChangePasswordRequest, *, db: Session) -> ChangePasswordResponse:
        user = self._get_user_by_email(db, payload.email)
        credentials = load_credentials(db, user.user_id_hash) if user is not None else None
        if user is None or credentials is None or not verify_password(payload.current_password, credentials.password_hash):
            raise ValueError("Invalid credentials.")
        if not user.is_active:
            raise PermissionError("User account is inactive.")

        now = datetime.utcnow()
        set_password(db, user, payload.new_password, now)
        user.updated_at = now
        db.add(user)
        db.commit()
        return ChangePasswordResponse(status="password_changed")

    def _get_user_by_email(self, db: Session, email: str) -> AuthUser | None:
        normalized_email = email.strip().lower()
        return db.execute(select(AuthUser).where(AuthUser.email == normalized_email)).scalar_one_or_none()
