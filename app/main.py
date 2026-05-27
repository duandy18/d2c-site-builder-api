from fastapi import FastAPI

from app.api.routes.admin.health import router as admin_health_router
from app.api.routes.admin.navigation import router as admin_navigation_router
from app.api.routes.runtime.health import router as runtime_health_router

app = FastAPI(title="D2C Site Builder API", version="0.1.0")

app.include_router(admin_health_router)
app.include_router(admin_navigation_router)
app.include_router(runtime_health_router)


@app.get("/system/health")
def system_health() -> dict[str, str]:
    return {
        "service": "d2c-site-builder-api",
        "status": "ok",
    }
