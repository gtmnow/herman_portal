from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_reset_token, hash_password, hash_reset_token
from app.models.auth_user import AuthUser
from app.models.auth_user_credential import AuthUserCredential
from app.models.password_reset_token import PasswordResetToken
from app.schemas.auth import ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse


class PasswordResetService:
    def request_reset(self, payload: ForgotPasswordRequest, *, db: Session) -> ForgotPasswordResponse:
        reset_token = generate_reset_token()
        reset_url = None
        user = self._get_user_by_email(db, payload.email)
        if user is not None and user.is_active:
            token_record = PasswordResetToken(
                user_id_hash=user.user_id_hash,
                token_hash=hash_reset_token(reset_token),
                expires_at=datetime.utcnow() + timedelta(seconds=settings.password_reset_token_ttl_seconds),
            )
            db.add(token_record)
            db.commit()

            if settings.dev_show_reset_links:
                reset_url = f"{settings.portal_ui_url}/reset-password?token={reset_token}"
        return ForgotPasswordResponse(status="accepted", reset_url=reset_url)

    def reset_password(self, payload: ResetPasswordRequest, *, db: Session) -> ResetPasswordResponse:
        token_hash = hash_reset_token(payload.token.strip())
        token_record = db.execute(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        ).scalar_one_or_none()

        if token_record is None:
            raise ValueError("Invalid reset token.")
        if token_record.used_at is not None:
            raise ValueError("Reset token has already been used.")
        if token_record.expires_at < datetime.utcnow():
            raise ValueError("Reset token has expired.")

        user = db.execute(
            select(AuthUser).where(AuthUser.user_id_hash == token_record.user_id_hash)
        ).scalar_one_or_none()
        if user is None or not user.is_active:
            raise ValueError("Invalid reset token.")

        credentials = db.get(AuthUserCredential, token_record.user_id_hash)
        if credentials is None:
            credentials = AuthUserCredential(user_id_hash=token_record.user_id_hash)

        credentials.password_hash = hash_password(payload.new_password)
        credentials.password_algorithm = "bcrypt"
        credentials.password_set_at = datetime.utcnow()
        credentials.failed_login_attempts = 0
        credentials.locked_until = None
        user.updated_at = datetime.utcnow()
        token_record.used_at = datetime.utcnow()

        db.add(credentials)
        db.add(user)
        db.add(token_record)
        db.commit()
        return ResetPasswordResponse(status="password_reset")

    def _get_user_by_email(self, db: Session, email: str) -> AuthUser | None:
        normalized_email = email.strip().lower()
        return db.execute(select(AuthUser).where(AuthUser.email == normalized_email)).scalar_one_or_none()
