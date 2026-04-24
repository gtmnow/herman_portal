from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError, URLError

from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    pass


class EmailService:
    def send_admin_mfa_code(self, *, email: str, code: str) -> None:
        self._send_email(
            email=email,
            subject="Your Herman Admin verification code",
            html=(
                "<p>Your Herman Admin verification code is:</p>"
                f"<p style=\"font-size: 28px; font-weight: 700; letter-spacing: 0.2em;\">{code}</p>"
                f"<p>This code expires in {settings.admin_mfa_code_ttl_seconds // 60} minutes.</p>"
            ),
            error_label="Admin MFA email delivery",
        )

    def send_password_reset_email(self, *, email: str, reset_url: str) -> None:
        self._send_email(
            email=email,
            subject="Reset your Herman Portal password",
            html=(
                "<p>We received a request to reset your Herman Portal password.</p>"
                f"<p><a href=\"{reset_url}\">Reset your password</a></p>"
                f"<p>This link expires in {settings.password_reset_token_ttl_seconds // 60} minutes.</p>"
                "<p>If you did not request this change, you can ignore this email.</p>"
            ),
            error_label="Password reset email delivery",
        )

    def _send_email(self, *, email: str, subject: str, html: str, error_label: str) -> None:
        api_key = (settings.resend_api_key or "").strip()
        if not api_key:
            raise EmailDeliveryError(f"{error_label} is not configured.")

        payload = {
            "from": f"{settings.admin_mfa_from_name} <{settings.admin_mfa_from_email}>",
            "to": [email],
            "subject": subject,
            "html": html,
        }
        if settings.admin_mfa_reply_to:
            payload["reply_to"] = settings.admin_mfa_reply_to

        req = request.Request(
            url=f"{settings.resend_api_base_url.rstrip('/')}/emails",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "herman-portal/1.0",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=15) as response:
                if response.status >= 400:
                    body = response.read().decode("utf-8", errors="replace").strip()
                    raise EmailDeliveryError(
                        f"{error_label} failed (HTTP {response.status})"
                        + (f": {body}" if body else ".")
                    )
        except HTTPError as exc:
            try:
                body = exc.read().decode("utf-8", errors="replace").strip()
            except Exception:  # pragma: no cover - defensive error parsing
                body = ""
            detail = f"{error_label} failed (HTTP {exc.code})"
            if body:
                detail = f"{detail}: {body}"
            raise EmailDeliveryError(detail) from exc
        except URLError as exc:
            reason = str(exc.reason).strip() if getattr(exc, "reason", None) else ""
            detail = f"{error_label} failed"
            if reason:
                detail = f"{detail}: {reason}"
            raise EmailDeliveryError(detail) from exc
