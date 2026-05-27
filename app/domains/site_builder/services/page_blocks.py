from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domains.site_builder.contracts.page_authoring_common import PageAuthoringBlockDto
from app.domains.site_builder.contracts.page_blocks import (
    CreateBlockRequest,
    UpdateBlockRequest,
)
from app.domains.site_builder.models.pc_home import SiteBuilderBlock
from app.domains.site_builder.repos.authoring_blocks import add_block, get_block
from app.domains.site_builder.repos.authoring_regions import get_region
from app.domains.site_builder.services.page_authoring_capabilities import (
    require_block_type_allowed,
)
from app.domains.site_builder.services.page_authoring_context import require_page_context
from app.domains.site_builder.services.page_codecs import next_block_code


def create_page_block(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
    region_code: str,
    request: CreateBlockRequest,
) -> PageAuthoringBlockDto:
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

    renderer_key = require_block_type_allowed(
        context.surface_code,
        region.region_type,
        request.block_type,
    )

    def exists(candidate: str) -> bool:
        return (
            get_block(
                session,
                context.site_code,
                context.surface_code,
                context.page_code,
                candidate,
            )
            is not None
        )

    block = SiteBuilderBlock(
        site_code=context.site_code,
        surface_code=context.surface_code,
        page_code=context.page_code,
        region_code=region.region_code,
        block_code=next_block_code(region.region_code, request.block_type, exists),
        block_name=request.block_name,
        block_type=request.block_type,
        renderer_key=renderer_key,
        sort_order=request.sort_order,
        content_json=request.content,
        layout_json=request.layout,
        status="active",
    )

    add_block(session, block)
    session.commit()
    session.refresh(block)

    return _block_to_dto(block)


def update_page_block(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
    block_code: str,
    request: UpdateBlockRequest,
) -> PageAuthoringBlockDto:
    context = require_page_context(session, site_code, surface_code, page_code)
    block = get_block(
        session,
        context.site_code,
        context.surface_code,
        context.page_code,
        block_code,
    )

    if not block:
        raise HTTPException(status_code=404, detail="block_not_found")

    if request.block_name is not None:
        block.block_name = request.block_name

    if request.sort_order is not None:
        block.sort_order = request.sort_order

    if request.content is not None:
        block.content_json = request.content

    if request.layout is not None:
        block.layout_json = request.layout

    if request.status is not None:
        block.status = request.status

    session.commit()
    session.refresh(block)

    return _block_to_dto(block)


def _block_to_dto(block: SiteBuilderBlock) -> PageAuthoringBlockDto:
    return PageAuthoringBlockDto(
        block_code=block.block_code,
        block_name=block.block_name,
        block_type=block.block_type,
        renderer_key=block.renderer_key,
        sort_order=block.sort_order,
        content=dict(block.content_json or {}),
        layout=dict(block.layout_json or {}),
        status=block.status,
    )
