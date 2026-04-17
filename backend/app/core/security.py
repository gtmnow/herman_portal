from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

from passlib.context import CryptContext

from app.core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_launch_token(*, external_user_id: str, display_name: str, tenant_id: str, user_id_hash: str) -> str:
    payload = {
        "external_user_id": external_user_id,
        "display_name": display_name,
        "tenant_id": tenant_id,
        "user_id_hash": user_id_hash,
        "exp": int(time.time()) + settings.launch_token_ttl_seconds,
    }
    encoded_payload = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = hmac.new(
        settings.hermanprompt_launch_secret.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{_b64url_encode(signature)}"


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")
