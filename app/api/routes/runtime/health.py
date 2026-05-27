from fastapi import APIRouter

router = APIRouter(prefix="/runtime/site-builder", tags=["runtime-health"])


@router.get("/health")
def runtime_health() -> dict[str, str]:
    return {
        "service": "d2c-site-builder-runtime",
        "status": "ok",
    }
