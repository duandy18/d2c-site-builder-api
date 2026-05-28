from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin.health import router as admin_health_router
from app.api.routes.admin.navigation import router as admin_navigation_router
from app.api.routes.admin.offer_resolve import router as offer_resolve_router
from app.api.routes.admin.page_authoring_blocks import router as page_blocks_router
from app.api.routes.admin.page_authoring_content import router as page_content_router
from app.api.routes.admin.page_authoring_draft import router as page_draft_router
from app.api.routes.admin.page_authoring_planner import router as page_planner_router
from app.api.routes.admin.page_authoring_regions import router as page_regions_router
from app.api.routes.admin.publish_readiness import router as publish_readiness_router
from app.api.routes.admin.publish_snapshot import router as publish_snapshot_router
from app.api.routes.admin.template_catalog import router as template_catalog_router
from app.api.routes.runtime.health import router as runtime_health_router
from app.api.routes.runtime.page_contract import router as runtime_page_contract_router
from app.core.config import get_settings

app = FastAPI(title="D2C Site Builder API", version="0.1.0")

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(admin_health_router)
app.include_router(admin_navigation_router)
app.include_router(offer_resolve_router)
app.include_router(template_catalog_router)
app.include_router(page_draft_router)
app.include_router(page_planner_router)
app.include_router(page_regions_router)
app.include_router(page_blocks_router)
app.include_router(page_content_router)
app.include_router(publish_readiness_router)
app.include_router(publish_snapshot_router)
app.include_router(runtime_health_router)
app.include_router(runtime_page_contract_router)


@app.get("/system/health")
def system_health() -> dict[str, str]:
    return {
        "service": "d2c-site-builder-api",
        "status": "ok",
    }
