from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_reset_token, hash_reset_token
from app.models.auth_user import AuthUser
from app.models.password_reset_token import PasswordResetToken
from app.schemas.auth import ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse
from app.services.credential_compat import set_password
from app.services.email_service import EmailDeliveryError, EmailService


class PasswordResetService:
    def __init__(self) -> None:
        self.email_service = EmailService()

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

            reset_url = f"{settings.portal_ui_url}/reset-password?token={reset_token}"
            if settings.resend_api_key:
                try:
                    self.email_service.send_password_reset_email(email=user.email, reset_url=reset_url)
                except EmailDeliveryError as exc:
                    raise ValueError(str(exc)) from exc
            elif not settings.allow_dev_reset_links:
                raise ValueError("Password reset email delivery is not configured.")

            if not settings.allow_dev_reset_links:
                reset_url = None
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

        now = datetime.utcnow()
        set_password(db, user, payload.new_password, now)
        user.updated_at = now
        token_record.used_at = now

        db.add(user)
        db.add(token_record)
        db.commit()
        return ResetPasswordResponse(status="password_reset")

    def _get_user_by_email(self, db: Session, email: str) -> AuthUser | None:
        normalized_email = email.strip().lower()
        return db.execute(
            select(AuthUser).where(func.lower(func.trim(AuthUser.email)) == normalized_email)
        ).scalar_one_or_none()
