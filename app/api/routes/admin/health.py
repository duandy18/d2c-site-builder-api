from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/admin/site-builder", tags=["admin-health"])


@router.get("/health")
def admin_health() -> dict[str, str]:
    settings = get_settings()
    return {
        "service": settings.service_name,
        "status": "ok",
        "environment": settings.environment,
    }
