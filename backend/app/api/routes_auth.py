from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth_user import AuthUser
from app.schemas.auth import (
    AcceptInvitationRequest,
    AcceptInvitationResponse,
    AppsResponse,
    BrandingResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    InvitationPreviewResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    PortalUserSummary,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.services.apps_service import AppsService
from app.services.auth_service import AuthService
from app.services.branding_service import BrandingService
from app.services.invitation_service import InvitationService
from app.services.launch_token_service import LaunchTokenService
from app.services.password_reset_service import PasswordResetService
from app.services.session_service import SessionService

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()
apps_service = AppsService()
branding_service = BrandingService()
invitation_service = InvitationService()
launch_token_service = LaunchTokenService()
password_reset_service = PasswordResetService()
session_service = SessionService()


def get_current_user(request: Request, db: Session = Depends(get_db)):
    return session_service.get_current_user(db=db, request=request)


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
async def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        login_response = auth_service.login(payload, db=db)
        auth_user = db.execute(
            select(AuthUser).where(AuthUser.user_id_hash == login_response.user.user_id_hash)
        ).scalar_one_or_none()
        if auth_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
        session_service.create_session(db=db, response=response, user=auth_user)
        db.commit()
        return login_response
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> LogoutResponse:
    session_service.clear_session(db=db, request=request, response=response)
    db.commit()
    return LogoutResponse()


@router.get("/me", response_model=PortalUserSummary)
async def me(user=Depends(get_current_user)) -> PortalUserSummary:
    return PortalUserSummary(
        email=user.email,
        user_id_hash=user.user_id_hash,
        display_name=user.display_name,
        tenant_id=user.tenant_id,
    )


@router.get("/apps", response_model=AppsResponse)
async def get_apps(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AppsResponse:
    return apps_service.get_available_apps(db=db, user=user)


@router.post("/launch/prompt", response_model=AcceptInvitationResponse)
async def launch_prompt(
    user=Depends(get_current_user),
) -> AcceptInvitationResponse:
    launch_token = launch_token_service.create_launch_token(
        external_user_id=f"auth_user:{user.user_id_hash}",
        display_name=user.display_name or user.email,
        tenant_id=user.tenant_id,
        user_id_hash=user.user_id_hash,
    )
    return AcceptInvitationResponse(
        launch_token=launch_token,
        redirect_url=launch_token_service.build_redirect_url(launch_token),
    )


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
