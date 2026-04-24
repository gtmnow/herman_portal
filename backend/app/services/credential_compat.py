from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.auth_user import AuthUser
from app.models.auth_user_credential import AuthUserCredential


@dataclass
class CredentialSnapshot:
    password_hash: str
    failed_login_attempts: int
    locked_until: datetime | None
    record: AuthUserCredential


def load_credentials(db: Session, user_id_hash: str) -> CredentialSnapshot | None:
    record = db.get(AuthUserCredential, user_id_hash)
    if record is None or not record.password_hash:
        return None

    return CredentialSnapshot(
        password_hash=record.password_hash,
        failed_login_attempts=record.failed_login_attempts,
        locked_until=record.locked_until,
        record=record,
    )


def record_failed_login(db: Session, credentials: CredentialSnapshot) -> None:
    credentials.record.failed_login_attempts += 1
    db.add(credentials.record)


def record_successful_login(db: Session, credentials: CredentialSnapshot, now: datetime) -> None:
    credentials.record.last_login_at = now
    credentials.record.failed_login_attempts = 0
    db.add(credentials.record)


def set_password(db: Session, user: AuthUser, new_password: str, now: datetime) -> None:
    password_hash = hash_password(new_password)

    record = db.get(AuthUserCredential, user.user_id_hash)
    if record is None:
        record = AuthUserCredential(user_id_hash=user.user_id_hash)
    record.password_hash = password_hash
    record.password_algorithm = "bcrypt"
    record.password_set_at = now
    record.failed_login_attempts = 0
    record.locked_until = None
    record.last_login_at = now
    db.add(record)
