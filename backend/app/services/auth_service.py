from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.auth_user import AuthUser
from app.schemas.auth import ChangePasswordRequest, ChangePasswordResponse, LoginRequest, LoginResponse
from app.services.launch_token_service import LaunchTokenService


class AuthService:
    def __init__(self) -> None:
        self.launch_token_service = LaunchTokenService()

    def login(self, payload: LoginRequest, *, db: Session) -> LoginResponse:
        user = self._get_user_by_email(db, payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise ValueError("Invalid credentials.")
        if not user.is_active:
            raise PermissionError("User account is inactive.")

        user.last_login_at = datetime.utcnow()
        db.add(user)
        db.commit()

        launch_token = self.launch_token_service.create_launch_token(
            external_user_id=f"auth_user:{user.id}",
            display_name=user.display_name or user.email,
            tenant_id=user.tenant_id,
            user_id_hash=user.user_id_hash,
        )
        return LoginResponse(
            launch_token=launch_token,
            redirect_url=self.launch_token_service.build_redirect_url(launch_token),
        )

    def change_password(self, payload: ChangePasswordRequest, *, db: Session) -> ChangePasswordResponse:
        user = self._get_user_by_email(db, payload.email)
        if user is None or not verify_password(payload.current_password, user.password_hash):
            raise ValueError("Invalid credentials.")
        if not user.is_active:
            raise PermissionError("User account is inactive.")

        user.password_hash = hash_password(payload.new_password)
        user.password_changed_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        return ChangePasswordResponse(status="password_changed")

    def _get_user_by_email(self, db: Session, email: str) -> AuthUser | None:
        normalized_email = email.strip().lower()
        return db.execute(select(AuthUser).where(AuthUser.email == normalized_email)).scalar_one_or_none()
