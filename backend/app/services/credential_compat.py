from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.auth_user import AuthUser
from app.models.auth_user_credential import AuthUserCredential


@dataclass
class CredentialSnapshot:
    password_hash: str
    failed_login_attempts: int
    locked_until: datetime | None
    backend: str
    record: AuthUserCredential | None = None


@lru_cache(maxsize=8)
def _has_credentials_table(database_url: str) -> bool:
    from sqlalchemy import create_engine

    engine = create_engine(database_url, future=True)
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'auth_user_credentials'
                LIMIT 1
                """
            )
        ).first()
    engine.dispose()
    return result is not None


def has_credentials_table(db: Session) -> bool:
    bind = db.get_bind()
    return _has_credentials_table(bind.url.render_as_string(hide_password=False))


def load_credentials(db: Session, user_id_hash: str) -> CredentialSnapshot | None:
    if has_credentials_table(db):
        record = db.get(AuthUserCredential, user_id_hash)
        if record is not None:
            return CredentialSnapshot(
                password_hash=record.password_hash,
                failed_login_attempts=record.failed_login_attempts,
                locked_until=record.locked_until,
                backend="auth_user_credentials",
                record=record,
            )

    row = db.execute(
        text(
            """
            SELECT password_hash
            FROM auth_users
            WHERE user_id_hash = :user_id_hash
            LIMIT 1
            """
        ),
        {"user_id_hash": user_id_hash},
    ).mappings().first()
    if row is None or not row["password_hash"]:
        return None

    return CredentialSnapshot(
        password_hash=row["password_hash"],
        failed_login_attempts=0,
        locked_until=None,
        backend="auth_users",
        record=None,
    )


def record_failed_login(db: Session, credentials: CredentialSnapshot) -> None:
    if credentials.backend != "auth_user_credentials" or credentials.record is None:
        return
    credentials.record.failed_login_attempts += 1
    db.add(credentials.record)


def record_successful_login(db: Session, credentials: CredentialSnapshot, now: datetime) -> None:
    if credentials.backend != "auth_user_credentials" or credentials.record is None:
        return
    credentials.record.last_login_at = now
    credentials.record.failed_login_attempts = 0
    db.add(credentials.record)


def set_password(db: Session, user: AuthUser, new_password: str, now: datetime) -> None:
    password_hash = hash_password(new_password)

    if has_credentials_table(db):
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
        return

    db.execute(
        text(
            """
            UPDATE auth_users
            SET password_hash = :password_hash,
                password_changed_at = :password_changed_at,
                updated_at = :updated_at
            WHERE user_id_hash = :user_id_hash
            """
        ),
        {
            "password_hash": password_hash,
            "password_changed_at": now,
            "updated_at": now,
            "user_id_hash": user.user_id_hash,
        },
    )
