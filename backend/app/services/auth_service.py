from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.auth_user import AuthUser
from app.models.auth_user_credential import AuthUserCredential
from app.schemas.auth import ChangePasswordRequest, ChangePasswordResponse, LoginRequest, LoginResponse
from app.services.launch_token_service import LaunchTokenService


class AuthService:
    def __init__(self) -> None:
        self.launch_token_service = LaunchTokenService()

    def login(self, payload: LoginRequest, *, db: Session) -> LoginResponse:
        user = self._get_user_by_email(db, payload.email)
        credentials = self._get_credentials(db, user.user_id_hash) if user is not None else None
        if user is None or credentials is None or not verify_password(payload.password, credentials.password_hash):
            if user is not None and credentials is not None:
                credentials.failed_login_attempts += 1
                db.add(credentials)
                db.commit()
            raise ValueError("Invalid credentials.")
        if not user.is_active:
            raise PermissionError("User account is inactive.")
        if credentials.locked_until is not None and credentials.locked_until > datetime.utcnow():
            raise PermissionError("User account is temporarily locked.")

        now = datetime.utcnow()
        user.last_login_at = now
        credentials.last_login_at = now
        credentials.failed_login_attempts = 0
        db.add(user)
        db.add(credentials)
        db.commit()

        launch_token = self.launch_token_service.create_launch_token(
            external_user_id=f"auth_user:{user.user_id_hash}",
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
        credentials = self._get_credentials(db, user.user_id_hash) if user is not None else None
        if user is None or credentials is None or not verify_password(payload.current_password, credentials.password_hash):
            raise ValueError("Invalid credentials.")
        if not user.is_active:
            raise PermissionError("User account is inactive.")

        credentials.password_hash = hash_password(payload.new_password)
        credentials.password_algorithm = "bcrypt"
        credentials.password_set_at = datetime.utcnow()
        credentials.failed_login_attempts = 0
        credentials.locked_until = None
        user.updated_at = datetime.utcnow()
        db.add(credentials)
        db.add(user)
        db.commit()
        return ChangePasswordResponse(status="password_changed")

    def _get_user_by_email(self, db: Session, email: str) -> AuthUser | None:
        normalized_email = email.strip().lower()
        return db.execute(select(AuthUser).where(AuthUser.email == normalized_email)).scalar_one_or_none()

    def _get_credentials(self, db: Session, user_id_hash: str) -> AuthUserCredential | None:
        return db.get(AuthUserCredential, user_id_hash)
