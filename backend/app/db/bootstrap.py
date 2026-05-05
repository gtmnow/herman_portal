from app.db.base import Base
from app.core.config import settings
from app.db.session import engine
from app.models import (
    AuthMfaChallenge,
    AuthSession,
    AuthUser,
    AuthUserCredential,
    PasswordResetToken,
)
from app.schema_contract import validate_schema_contract


def initialize_database() -> None:
    if settings.effective_herman_db_canonical_mode:
        validate_schema_contract(
            engine=engine,
            version_table=settings.herman_db_version_table,
            allowed_revisions=settings.herman_db_allowed_revisions,
        )
        return

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
