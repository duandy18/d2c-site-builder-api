from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.page_authoring_common import PageAuthoringRegionDto
from app.domains.site_builder.contracts.page_regions import (
    CreateRegionRequest,
    UpdateRegionRequest,
)
from app.domains.site_builder.services.page_regions import (
    create_page_region,
    update_page_region,
)

router = APIRouter(
    prefix="/admin/site-builder/sites/{site_code}/surfaces/{surface_code}/pages/{page_code}",
    tags=["page-authoring-regions"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/regions", response_model=PageAuthoringRegionDto)
def create_region(
    site_code: str,
    surface_code: str,
    page_code: str,
    request: CreateRegionRequest,
    session: SessionDep,
) -> PageAuthoringRegionDto:
    return create_page_region(session, site_code, surface_code, page_code, request)


@router.patch("/regions/{region_code}", response_model=PageAuthoringRegionDto)
def update_region(
    site_code: str,
    surface_code: str,
    page_code: str,
    region_code: str,
    request: UpdateRegionRequest,
    session: SessionDep,
) -> PageAuthoringRegionDto:
    return update_page_region(
        session,
        site_code,
        surface_code,
        page_code,
        region_code,
        request,
    )
