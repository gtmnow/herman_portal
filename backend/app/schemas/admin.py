from pydantic import BaseModel, EmailStr


class AdminUserCreateRequest(BaseModel):
    email: EmailStr
    user_id_hash: str
    display_name: str | None = None


class AdminUserUpdateRequest(BaseModel):
    display_name: str | None = None
    user_id_hash: str | None = None
    is_active: bool | None = None
