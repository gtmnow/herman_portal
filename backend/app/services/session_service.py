from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_session_token, hash_session_token
from app.models.auth_session import AuthSession
from app.models.auth_user import AuthUser


@dataclass
class SessionContext:
    user: AuthUser
    session: AuthSession


class SessionService:
    def create_session(self, *, db: Session, response: Response, user: AuthUser) -> str:
        now = datetime.utcnow()
        raw_token = generate_session_token()
        session_record = AuthSession(
            session_token_hash=hash_session_token(raw_token),
            user_id_hash=user.user_id_hash,
            expires_at=now + timedelta(seconds=settings.portal_session_ttl_seconds),
            revoked_at=None,
            created_at=now,
            last_seen_at=now,
        )
        db.add(session_record)
        self._set_session_cookie(response, raw_token)
        return raw_token

    def clear_session(self, *, db: Session, request: Request, response: Response) -> None:
        raw_token = self._get_session_token_from_request(request)
        if raw_token:
            session_record = db.get(AuthSession, hash_session_token(raw_token))
            if session_record is not None and session_record.revoked_at is None:
                session_record.revoked_at = datetime.utcnow()
                db.add(session_record)
        response.delete_cookie(
            key=settings.portal_session_cookie_name,
            httponly=True,
            samesite=settings.effective_portal_session_same_site,
            secure=settings.effective_portal_session_secure,
            path="/",
        )

    def get_current_context(self, *, db: Session, request: Request) -> SessionContext:
        raw_token = self._get_session_token_from_request(request)
        if not raw_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

        now = datetime.utcnow()
        session_record = db.get(AuthSession, hash_session_token(raw_token))
        if session_record is None or session_record.revoked_at is not None or session_record.expires_at <= now:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

        user = db.execute(select(AuthUser).where(AuthUser.user_id_hash == session_record.user_id_hash)).scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

        session_record.last_seen_at = now
        db.add(session_record)
        db.commit()
        db.refresh(user)
        return SessionContext(user=user, session=session_record)

    def get_current_user(self, *, db: Session, request: Request) -> AuthUser:
        return self.get_current_context(db=db, request=request).user

    def _set_session_cookie(self, response: Response, raw_token: str) -> None:
        response.set_cookie(
            key=settings.portal_session_cookie_name,
            value=raw_token,
            max_age=settings.portal_session_ttl_seconds,
            httponly=True,
            samesite=settings.effective_portal_session_same_site,
            secure=settings.effective_portal_session_secure,
            path="/",
        )

    def _get_session_token_from_request(self, request: Request) -> str | None:
        cookie_token = request.cookies.get(settings.portal_session_cookie_name)
        if cookie_token:
            return cookie_token

        header_token = request.headers.get("X-Portal-Session")
        if header_token:
            return header_token.strip() or None

        authorization = request.headers.get("Authorization")
        if not authorization:
            return None

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            return None
        return token.strip() or None
