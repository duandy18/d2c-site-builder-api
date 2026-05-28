from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.publish_readiness import (
    PublishReadinessResponse,
)
from app.domains.site_builder.services.publish_readiness import (
    build_publish_readiness,
)

router = APIRouter(
    prefix="/admin/site-builder/sites/{site_code}/surfaces/{surface_code}/pages/{page_code}",
    tags=["publish-readiness"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/publish-readiness", response_model=PublishReadinessResponse)
def get_page_publish_readiness(
    site_code: str,
    surface_code: str,
    page_code: str,
    session: SessionDep,
) -> PublishReadinessResponse:
    return build_publish_readiness(session, site_code, surface_code, page_code)
