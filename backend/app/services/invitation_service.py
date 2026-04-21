from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_invitation_token, hash_password
from app.models.auth_user import AuthUser
from app.models.auth_user_credential import AuthUserCredential
from app.schemas.auth import AcceptInvitationRequest, AcceptInvitationResponse, InvitationPreviewResponse
from app.services.branding_service import BrandingService
from app.services.launch_token_service import LaunchTokenService

ACCEPTABLE_INVITATION_STATUSES = {"pending", "sent"}


@dataclass
class InvitationRecord:
    invite_token_hash: str
    user_id_hash: str
    tenant_id: str
    email: str
    status: str
    expires_at: datetime | None
    accepted_at: datetime | None
    revoked_at: datetime | None


class InvitationService:
    def __init__(self) -> None:
        self.branding_service = BrandingService()
        self.launch_token_service = LaunchTokenService()

    def preview_invitation(self, token: str, *, db: Session) -> InvitationPreviewResponse:
        invitation = self._find_invitation(token, db=db)
        if invitation is None:
            return self._invalid_preview()

        validation_error = self._get_invitation_validation_error(invitation)
        branding = self.branding_service.get_branding(db=db, tenant_id=invitation.tenant_id)
        if validation_error is not None:
            return InvitationPreviewResponse(
                status="invalid",
                email=None,
                tenant_id=invitation.tenant_id,
                logo_url=branding.logo_url,
                welcome_message=branding.welcome_message,
                error=validation_error,
            )

        return InvitationPreviewResponse(
            status="ready",
            email=invitation.email,
            tenant_id=invitation.tenant_id,
            logo_url=branding.logo_url,
            welcome_message=branding.welcome_message,
            error=None,
        )

    def accept_invitation(self, payload: AcceptInvitationRequest, *, db: Session) -> AcceptInvitationResponse:
        invitation = self._find_invitation(payload.token, db=db)
        if invitation is None:
            raise ValueError("Invitation link is invalid.")

        validation_error = self._get_invitation_validation_error(invitation)
        if validation_error is not None:
            raise ValueError(validation_error)

        user = db.execute(
            select(AuthUser).where(AuthUser.user_id_hash == invitation.user_id_hash)
        ).scalar_one_or_none()
        if user is None:
            raise ValueError("Invitation user could not be resolved.")

        normalized_email = invitation.email.strip().lower()
        if user.email != normalized_email:
            raise ValueError("Invitation email does not match the mapped user.")

        now = datetime.utcnow()
        credentials = db.get(AuthUserCredential, invitation.user_id_hash)
        if credentials is None:
            credentials = AuthUserCredential(user_id_hash=invitation.user_id_hash)

        credentials.password_hash = hash_password(payload.new_password)
        credentials.password_algorithm = "bcrypt"
        credentials.password_set_at = now
        credentials.failed_login_attempts = 0
        credentials.locked_until = None
        credentials.last_login_at = now

        user.is_active = True
        user.updated_at = now
        user.last_login_at = now

        db.add(credentials)
        db.add(user)
        self._mark_invitation_accepted(db, invitation.invite_token_hash, now)
        db.commit()

        launch_token = self.launch_token_service.create_launch_token(
            external_user_id=f"auth_user:{user.user_id_hash}",
            display_name=user.display_name or user.email,
            tenant_id=user.tenant_id,
            user_id_hash=user.user_id_hash,
        )
        return AcceptInvitationResponse(
            launch_token=launch_token,
            redirect_url=self.launch_token_service.build_redirect_url(launch_token),
        )

    def _find_invitation(self, token: str, *, db: Session) -> InvitationRecord | None:
        normalized_token = token.strip()
        if not normalized_token:
            return None

        token_hash = hash_invitation_token(normalized_token)
        queries = [
            text(
                """
                SELECT invite_token_hash, user_id_hash, tenant_id, email, status, expires_at, accepted_at, revoked_at
                FROM user_invitations
                WHERE invite_token_hash = :token_hash
                LIMIT 1
                """
            ),
            text(
                """
                SELECT invite_token_hash, user_id_hash, tenant_id, email, status, expires_at, accepted_at, revoked_at
                FROM user_invitations
                WHERE invite_token = :token_hash
                LIMIT 1
                """
            ),
        ]

        for query in queries:
            try:
                row = db.execute(query, {"token_hash": token_hash}).mappings().first()
            except Exception:
                continue
            if row is not None:
                return InvitationRecord(**dict(row))

        return None

    def _get_invitation_validation_error(self, invitation: InvitationRecord) -> str | None:
        if invitation.status not in ACCEPTABLE_INVITATION_STATUSES:
            return "This invitation is no longer available."
        if invitation.revoked_at is not None:
            return "This invitation has been revoked."
        expires_at = invitation.expires_at
        if expires_at is None:
            return (
                "This invitation is missing an expiration timestamp. "
                f"Expected admin-managed expiry within {settings.invitation_token_fallback_ttl_seconds} seconds."
            )
        if expires_at < datetime.utcnow():
            return "This invitation has expired."
        if invitation.accepted_at is not None:
            return "This invitation has already been used."
        return None

    def _mark_invitation_accepted(self, db: Session, invite_token_hash: str, accepted_at: datetime) -> None:
        db.execute(
            text(
                """
                UPDATE user_invitations
                SET status = 'accepted', accepted_at = :accepted_at
                WHERE invite_token_hash = :invite_token_hash
                """
            ),
            {
                "accepted_at": accepted_at,
                "invite_token_hash": invite_token_hash,
            },
        )

    def _invalid_preview(self) -> InvitationPreviewResponse:
        return InvitationPreviewResponse(
            status="invalid",
            email=None,
            tenant_id=None,
            logo_url=None,
            welcome_message=settings.default_welcome_message,
            error="This invitation link is invalid or no longer available.",
        )
