from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    AcceptInvitationRequest,
    AcceptInvitationResponse,
    BrandingResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    InvitationPreviewResponse,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.services.auth_service import AuthService
from app.services.branding_service import BrandingService
from app.services.invitation_service import InvitationService
from app.services.password_reset_service import PasswordResetService

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()
branding_service = BrandingService()
invitation_service = InvitationService()
password_reset_service = PasswordResetService()


@router.get("/branding", response_model=BrandingResponse)
async def get_branding(
    tenant_id: str | None = Query(default=None),
    tenant: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> BrandingResponse:
    return branding_service.get_branding(db=db, tenant_id=tenant_id or tenant)


@router.get("/invite", response_model=InvitationPreviewResponse)
async def preview_invitation(
    token: str = Query(min_length=1),
    db: Session = Depends(get_db),
) -> InvitationPreviewResponse:
    return invitation_service.preview_invitation(token, db=db)


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        return auth_service.login(payload, db=db)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/accept-invite", response_model=AcceptInvitationResponse)
async def accept_invitation(
    payload: AcceptInvitationRequest,
    db: Session = Depends(get_db),
) -> AcceptInvitationResponse:
    try:
        return invitation_service.accept_invitation(payload, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> ForgotPasswordResponse:
    return password_reset_service.request_reset(payload, db=db)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> ResetPasswordResponse:
    try:
        return password_reset_service.reset_password(payload, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
) -> ChangePasswordResponse:
    try:
        return auth_service.change_password(payload, db=db)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
