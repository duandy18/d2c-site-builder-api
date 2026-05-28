from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.publish_snapshot import (
    PublishPageRequest,
    PublishPageResponse,
)
from app.domains.site_builder.services.publish_snapshot import publish_page_snapshot

router = APIRouter(
    prefix="/admin/site-builder/sites/{site_code}/surfaces/{surface_code}/pages/{page_code}",
    tags=["publish-snapshot"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/publish", response_model=PublishPageResponse)
def publish_page(
    site_code: str,
    surface_code: str,
    page_code: str,
    request: PublishPageRequest,
    session: SessionDep,
) -> PublishPageResponse:
    return publish_page_snapshot(session, site_code, surface_code, page_code, request)
