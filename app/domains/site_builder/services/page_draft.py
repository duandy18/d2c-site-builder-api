from collections import defaultdict

from sqlalchemy.orm import Session

from app.domains.site_builder.contracts.page_authoring_common import (
    PageAuthoringBlockDto,
    PageAuthoringRegionDto,
)
from app.domains.site_builder.contracts.page_draft import PageDraftResponse
from app.domains.site_builder.models.pc_home import SiteBuilderBlock
from app.domains.site_builder.repos.authoring_blocks import list_blocks
from app.domains.site_builder.repos.authoring_regions import list_regions
from app.domains.site_builder.services.page_authoring_context import require_page_context


def build_page_draft(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> PageDraftResponse:
    context = require_page_context(session, site_code, surface_code, page_code)

    regions = list_regions(
        session,
        context.site_code,
        context.surface_code,
        context.page_code,
    )
    blocks = list_blocks(
        session,
        context.site_code,
        context.surface_code,
        context.page_code,
    )

    blocks_by_region: dict[str, list[SiteBuilderBlock]] = defaultdict(list)
    for block in blocks:
        blocks_by_region[block.region_code].append(block)

    region_dtos = [
        PageAuthoringRegionDto(
            region_code=region.region_code,
            region_name=region.region_name,
            region_type=region.region_type,
            template_region_code=region.region_type,
            sort_order=region.sort_order,
            status=region.status,
            blocks=[
                PageAuthoringBlockDto(
                    block_code=block.block_code,
                    block_name=block.block_name,
                    block_type=block.block_type,
                    renderer_key=block.renderer_key,
                    sort_order=block.sort_order,
                    content=dict(block.content_json or {}),
                    presentation=dict(block.presentation_json or {}),
                    status=block.status,
                )
                for block in blocks_by_region[region.region_code]
            ],
        )
        for region in regions
    ]

    return PageDraftResponse(
        site_code=context.site_code,
        surface_code=context.surface_code,
        page_code=context.page_code,
        page_title=context.page_title,
        template_key=context.template_key,
        template_name=context.template_name,
        regions=region_dtos,
    )
