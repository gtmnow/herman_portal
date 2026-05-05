from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_admin import router as admin_router
from app.api.routes_auth import router as auth_router
from app.core.config import settings
from app.db.session import engine
from app.schema_contract import validate_schema_contract


def create_app() -> FastAPI:
    app = FastAPI(title="Herman Portal API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.on_event("startup")
    def startup() -> None:
        if settings.effective_herman_db_canonical_mode:
            validate_schema_contract(
                engine=engine,
                version_table=settings.herman_db_version_table,
                allowed_revisions=settings.herman_db_allowed_revisions,
            )

    app.include_router(auth_router)
    app.include_router(admin_router)
    return app


app = create_app()
