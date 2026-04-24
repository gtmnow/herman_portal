from app.db.base import Base
from app.db.session import engine
from app.models import (
    AuthMfaChallenge,
    AuthSession,
    AuthUser,
    AuthUserCredential,
    PasswordResetToken,
)


def initialize_database() -> None:
    # Only create portal-owned auth tables here. Shared Admin-owned tables such
    # as `tenant_portal_configs` and `user_invitations` must come from their
    # canonical migration owner to avoid cross-repo schema drift.
    _ = (
        AuthMfaChallenge,
        AuthSession,
        AuthUser,
        AuthUserCredential,
        PasswordResetToken,
    )
    Base.metadata.create_all(
        bind=engine,
        tables=[
            AuthUser.__table__,
            AuthUserCredential.__table__,
            PasswordResetToken.__table__,
            AuthSession.__table__,
            AuthMfaChallenge.__table__,
        ],
    )
