from app.schemas.auth import LoginRequest, LoginResponse
from app.services.launch_token_service import LaunchTokenService


class AuthService:
    def __init__(self) -> None:
        self.launch_token_service = LaunchTokenService()

    def login(self, payload: LoginRequest) -> LoginResponse:
        # Scaffold only. Replace with real DB lookup and password verification.
        if payload.email.lower() != "demo@example.com" or payload.password != "password123":
            raise ValueError("Invalid credentials.")

        launch_token = self.launch_token_service.create_launch_token(
            external_user_id="auth_user:demo",
            display_name="Demo User",
            tenant_id="tenant_demo",
            user_id_hash="user_1",
        )
        return LoginResponse(
            launch_token=launch_token,
            redirect_url=self.launch_token_service.build_redirect_url(launch_token),
        )
