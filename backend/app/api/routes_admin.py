from fastapi import APIRouter

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/hooks")
async def admin_hooks() -> dict[str, list[str]]:
    return {
        "planned_routes": [
            "POST /api/admin/users",
            "PATCH /api/admin/users/{id}",
            "DELETE /api/admin/users/{id}",
            "POST /api/admin/users/{id}/reset-password",
            "POST /api/admin/users/{id}/deactivate",
        ]
    }
