from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError, URLError

from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    pass


class EmailService:
    def send_admin_mfa_code(self, *, email: str, code: str) -> None:
        api_key = (settings.resend_api_key or "").strip()
        if not api_key:
            raise EmailDeliveryError("Admin MFA email delivery is not configured.")

        payload = {
            "from": f"{settings.admin_mfa_from_name} <{settings.admin_mfa_from_email}>",
            "to": [email],
            "subject": "Your Herman Admin verification code",
            "html": (
                "<p>Your Herman Admin verification code is:</p>"
                f"<p style=\"font-size: 28px; font-weight: 700; letter-spacing: 0.2em;\">{code}</p>"
                f"<p>This code expires in {settings.admin_mfa_code_ttl_seconds // 60} minutes.</p>"
            ),
        }
        if settings.admin_mfa_reply_to:
            payload["reply_to"] = settings.admin_mfa_reply_to

        req = request.Request(
            url=f"{settings.resend_api_base_url.rstrip('/')}/emails",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=15) as response:
                if response.status >= 400:
                    body = response.read().decode("utf-8", errors="replace").strip()
                    raise EmailDeliveryError(
                        f"Admin MFA email delivery failed (HTTP {response.status})"
                        + (f": {body}" if body else ".")
                    )
        except HTTPError as exc:
            try:
                body = exc.read().decode("utf-8", errors="replace").strip()
            except Exception:  # pragma: no cover - defensive error parsing
                body = ""
            detail = f"Admin MFA email delivery failed (HTTP {exc.code})"
            if body:
                detail = f"{detail}: {body}"
            raise EmailDeliveryError(detail) from exc
        except URLError as exc:
            reason = str(exc.reason).strip() if getattr(exc, "reason", None) else ""
            detail = "Admin MFA email delivery failed"
            if reason:
                detail = f"{detail}: {reason}"
            raise EmailDeliveryError(detail) from exc
