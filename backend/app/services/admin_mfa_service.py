from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_mfa_code, hash_mfa_code
from app.models.auth_mfa_challenge import AuthMfaChallenge
from app.models.auth_session import AuthSession
from app.models.auth_user import AuthUser
from app.schemas.auth import AdminMfaRequestResponse, AdminMfaVerifyResponse
from app.services.email_service import EmailDeliveryError, EmailService


class AdminMfaService:
    def __init__(self) -> None:
        self.email_service = EmailService()

    def request_code(
        self,
        *,
        db: Session,
        user: AuthUser,
        portal_session: AuthSession,
    ) -> AdminMfaRequestResponse:
        now = datetime.utcnow()
        code = generate_mfa_code()
        challenge = AuthMfaChallenge(
            user_id_hash=user.user_id_hash,
            challenge_type="email_code",
            requested_app="herman_admin",
            code_hash=hash_mfa_code(code),
            expires_at=now + timedelta(seconds=settings.admin_mfa_code_ttl_seconds),
            consumed_at=None,
            attempt_count=0,
            created_at=now,
        )
        portal_session.admin_mfa_verified_at = None
        db.add(challenge)
        db.add(portal_session)

        dev_code: str | None = None
        if settings.resend_api_key:
            try:
                self.email_service.send_admin_mfa_code(email=user.email, code=code)
            except EmailDeliveryError as exc:
                raise ValueError(str(exc)) from exc
        elif settings.allow_dev_mfa_codes:
            dev_code = code
        else:
            raise ValueError("Admin MFA email delivery is not configured.")

        db.commit()
        return AdminMfaRequestResponse(
            status="code_sent",
            expires_in_seconds=settings.admin_mfa_code_ttl_seconds,
            dev_code=dev_code,
        )

    def verify_code(
        self,
        *,
        db: Session,
        user: AuthUser,
        portal_session: AuthSession,
        code: str,
    ) -> AdminMfaVerifyResponse:
        now = datetime.utcnow()
        challenge = db.execute(self._active_challenge_query(user_id_hash=user.user_id_hash, now=now)).scalar_one_or_none()
        if challenge is None:
            raise ValueError("No active Admin MFA challenge was found. Request a new code.")
        if challenge.attempt_count >= settings.admin_mfa_max_attempts:
            raise ValueError("Too many invalid verification attempts. Request a new code.")

        challenge.attempt_count += 1
        if challenge.code_hash != hash_mfa_code(code.strip()):
            db.add(challenge)
            db.commit()
            raise ValueError("Invalid verification code.")

        challenge.consumed_at = now
        portal_session.admin_mfa_verified_at = now
        db.add(challenge)
        db.add(portal_session)
        db.commit()
        return AdminMfaVerifyResponse(
            status="verified",
            verified_for_seconds=settings.admin_mfa_verified_ttl_seconds,
        )

    def ensure_recent_verification(self, *, portal_session: AuthSession) -> None:
        verified_at = portal_session.admin_mfa_verified_at
        if verified_at is None:
            raise ValueError("Admin launch requires MFA verification.")
        if verified_at + timedelta(seconds=settings.admin_mfa_verified_ttl_seconds) < datetime.utcnow():
            raise ValueError("Admin MFA verification expired. Request a new code.")

    def _active_challenge_query(self, *, user_id_hash: str, now: datetime) -> Select[tuple[AuthMfaChallenge]]:
        return (
            select(AuthMfaChallenge)
            .where(
                AuthMfaChallenge.user_id_hash == user_id_hash,
                AuthMfaChallenge.requested_app == "herman_admin",
                AuthMfaChallenge.consumed_at.is_(None),
                AuthMfaChallenge.expires_at > now,
            )
            .order_by(AuthMfaChallenge.created_at.desc())
            .limit(1)
        )
