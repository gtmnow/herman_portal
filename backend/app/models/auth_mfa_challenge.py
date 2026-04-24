from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuthMfaChallenge(Base):
    __tablename__ = "auth_mfa_challenges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id_hash: Mapped[str] = mapped_column(String(255), index=True)
    challenge_type: Mapped[str] = mapped_column(String(64), default="email_code")
    requested_app: Mapped[str] = mapped_column(String(64), index=True, default="herman_admin")
    code_hash: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
