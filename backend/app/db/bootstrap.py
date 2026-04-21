from app.db.base import Base
from app.db.session import engine
from app.models import AuthUser, AuthUserCredential, PasswordResetToken, TenantPortalConfig, UserInvitation


def initialize_database() -> None:
    # Importing model symbols ensures SQLAlchemy metadata is fully registered
    # before create_all runs in local/dev bootstrap flows.
    _ = (AuthUser, AuthUserCredential, PasswordResetToken, TenantPortalConfig, UserInvitation)
    Base.metadata.create_all(bind=engine)
