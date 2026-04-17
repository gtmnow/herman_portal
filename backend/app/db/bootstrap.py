from app.db.base import Base
from app.db.session import engine
from app.models import AuthUser, PasswordResetToken


def initialize_database() -> None:
    # Importing model symbols ensures SQLAlchemy metadata is fully registered
    # before create_all runs in local/dev bootstrap flows.
    _ = (AuthUser, PasswordResetToken)
    Base.metadata.create_all(bind=engine)
