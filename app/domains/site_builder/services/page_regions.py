from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domains.site_builder.contracts.page_authoring_common import PageAuthoringRegionDto
from app.domains.site_builder.contracts.page_regions import (
    CreateRegionRequest,
    UpdateRegionRequest,
)
from app.domains.site_builder.models.pc_home import SiteBuilderRegion
from app.domains.site_builder.repos.authoring_regions import (
    add_region,
    get_region,
    list_regions,
)
from app.domains.site_builder.services.page_authoring_capabilities import require_template_region
from app.domains.site_builder.services.page_authoring_context import require_page_context
from app.domains.site_builder.services.page_codecs import next_region_code


def create_page_region(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
    request: CreateRegionRequest,
) -> PageAuthoringRegionDto:
    context = require_page_context(session, site_code, surface_code, page_code)
    template_region = require_template_region(
        context.template_key,
        request.template_region_code,
    )

    existing_regions = list_regions(
        session,
        context.site_code,
        context.surface_code,
        context.page_code,
    )

    template_region_already_enabled = any(
        region.region_type == template_region.template_region_code
        for region in existing_regions
    )

    if template_region_already_enabled:
        raise HTTPException(status_code=409, detail="template_region_already_enabled")

    def exists(candidate: str) -> bool:
        return (
            get_region(
                session,
                context.site_code,
                context.surface_code,
                context.page_code,
                candidate,
            )
            is not None
        )

    region = SiteBuilderRegion(
        site_code=context.site_code,
        surface_code=context.surface_code,
        page_code=context.page_code,
        region_code=next_region_code(
            context.page_code,
            template_region.template_region_code,
            exists,
        ),
        region_name=request.region_name or template_region.default_region_name,
        region_type=template_region.template_region_code,
        sort_order=request.sort_order or template_region.sort_order,
        status="active",
    )

    add_region(session, region)
    session.commit()
    session.refresh(region)

    return _region_to_dto(region)


def update_page_region(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
    region_code: str,
    request: UpdateRegionRequest,
) -> PageAuthoringRegionDto:
    context = require_page_context(session, site_code, surface_code, page_code)
    region = get_region(
        session,
        context.site_code,
        context.surface_code,
        context.page_code,
        region_code,
    )

    if not region:
        raise HTTPException(status_code=404, detail="region_not_found")

    if request.region_name is not None:
        region.region_name = request.region_name

    if request.sort_order is not None:
        region.sort_order = request.sort_order

    if request.status is not None:
        region.status = request.status

    session.commit()
    session.refresh(region)

    return _region_to_dto(region)


def _region_to_dto(region: SiteBuilderRegion) -> PageAuthoringRegionDto:
    return PageAuthoringRegionDto(
        region_code=region.region_code,
        region_name=region.region_name,
        region_type=region.region_type,
        template_region_code=region.region_type,
        sort_order=region.sort_order,
        status=region.status,
        blocks=[],
    )
