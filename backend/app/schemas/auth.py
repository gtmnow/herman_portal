from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginResponse(BaseModel):
    launch_token: str
    redirect_url: str


class BrandingResponse(BaseModel):
    tenant_id: str | None = None
    logo_url: str | None = None
    welcome_message: str
    portal_base_url: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    status: str = "accepted"
    reset_url: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8)


class ResetPasswordResponse(BaseModel):
    status: str = "password_reset"


class InvitationPreviewResponse(BaseModel):
    status: str
    email: EmailStr | None = None
    tenant_id: str | None = None
    logo_url: str | None = None
    welcome_message: str
    error: str | None = None


class AcceptInvitationRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8)


class AcceptInvitationResponse(BaseModel):
    launch_token: str
    redirect_url: str


class ChangePasswordRequest(BaseModel):
    email: EmailStr
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class ChangePasswordResponse(BaseModel):
    status: str = "password_changed"
