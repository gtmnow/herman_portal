from app.core.config import settings
from app.core.security import generate_reset_token
from app.schemas.auth import ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse


class PasswordResetService:
    def request_reset(self, payload: ForgotPasswordRequest) -> ForgotPasswordResponse:
        reset_token = generate_reset_token()
        reset_url = None
        if settings.dev_show_reset_links:
            reset_url = f"{settings.hermanprompt_ui_url.replace(':5173', ':5174')}/reset-password?token={reset_token}"
        return ForgotPasswordResponse(status="accepted", reset_url=reset_url)

    def reset_password(self, payload: ResetPasswordRequest) -> ResetPasswordResponse:
        if not payload.token.strip():
            raise ValueError("Invalid reset token.")
        return ResetPasswordResponse(status="password_reset")
