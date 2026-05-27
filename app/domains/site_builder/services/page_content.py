from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domains.site_builder.contracts.page_content import (
    PageContentFormResponse,
    PageContentRegionGroupDto,
    PageContentSlotDto,
    SlotContentResponse,
    UpdateSlotContentRequest,
)
from app.domains.site_builder.models.pc_home import SiteBuilderBlock, SiteBuilderRegion
from app.domains.site_builder.repos.authoring_blocks import add_block, get_block, list_blocks
from app.domains.site_builder.repos.authoring_regions import (
    add_region,
    list_regions,
)
from app.domains.site_builder.services.page_authoring_capabilities import (
    BlockSlotCapability,
    TemplateRegionCapability,
    content_field_to_dto,
    get_renderer_key,
    list_template_region_options,
    require_block_slot,
)
from app.domains.site_builder.services.page_authoring_context import (
    PageAuthoringContext,
    require_page_context,
)
from app.domains.site_builder.services.page_codecs import next_region_code


def build_page_content_form(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> PageContentFormResponse:
    context = require_page_context(session, site_code, surface_code, page_code)
    blocks_by_code = {
        block.block_code: block
        for block in list_blocks(
            session,
            context.site_code,
            context.surface_code,
            context.page_code,
        )
    }

    groups = [
        PageContentRegionGroupDto(
            template_region_code=template_region.template_region_code,
            label=template_region.label,
            description=template_region.description,
            required=template_region.required,
            default_region_name=template_region.default_region_name,
            sort_order=template_region.sort_order,
            slots=[
                _slot_to_form_dto(
                    context,
                    slot,
                    blocks_by_code.get(_block_code_for_slot(context, slot)),
                )
                for slot in template_region.block_slots
            ],
        )
        for template_region in list_template_region_options(
            context.template_key,
            context.surface_code,
        )
    ]

    return PageContentFormResponse(
        site_code=context.site_code,
        surface_code=context.surface_code,
        page_code=context.page_code,
        page_title=context.page_title,
        template_key=context.template_key,
        template_name=context.template_name,
        groups=groups,
    )


def update_slot_content(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
    slot_code: str,
    request: UpdateSlotContentRequest,
) -> SlotContentResponse:
    context = require_page_context(session, site_code, surface_code, page_code)
    template_region, slot = require_block_slot(context.template_key, slot_code)

    _validate_content(slot, request.content)

    region = _ensure_template_region(session, context, template_region)
    block_code = _block_code_for_slot(context, slot)
    block = get_block(
        session,
        context.site_code,
        context.surface_code,
        context.page_code,
        block_code,
    )

    if block is None:
        block = SiteBuilderBlock(
            site_code=context.site_code,
            surface_code=context.surface_code,
            page_code=context.page_code,
            region_code=region.region_code,
            block_code=block_code,
            block_name=slot.default_block_name,
            block_type=slot.block_type,
            renderer_key=get_renderer_key(context.surface_code, slot.block_type),
            sort_order=slot.sort_order,
            content_json=request.content,
            layout_json={},
            status="active",
        )
        add_block(session, block)
    else:
        block.content_json = request.content
        block.status = "active"

    session.commit()
    session.refresh(block)

    return SlotContentResponse(
        slot_code=slot.slot_code,
        block_code=block.block_code,
        block_type=block.block_type,
        renderer_key=block.renderer_key,
        content=dict(block.content_json or {}),
        status=block.status,
    )


def _block_code_for_slot(
    context: PageAuthoringContext,
    slot: BlockSlotCapability,
) -> str:
    return f"{context.page_code}.{slot.slot_code}"


def _slot_to_form_dto(
    context: PageAuthoringContext,
    slot: BlockSlotCapability,
    block: SiteBuilderBlock | None,
) -> PageContentSlotDto:
    return PageContentSlotDto(
        slot_code=slot.slot_code,
        label=slot.label,
        description=slot.description,
        block_type=slot.block_type,
        renderer_key=get_renderer_key(context.surface_code, slot.block_type),
        required=slot.required,
        default_block_name=slot.default_block_name,
        sort_order=slot.sort_order,
        content_fields=[content_field_to_dto(field) for field in slot.content_fields],
        block_code=block.block_code if block else None,
        status=block.status if block else None,
        content=dict(block.content_json or {}) if block else {},
    )


def _ensure_template_region(
    session: Session,
    context: PageAuthoringContext,
    template_region: TemplateRegionCapability,
) -> SiteBuilderRegion:
    existing_regions = list_regions(
        session,
        context.site_code,
        context.surface_code,
        context.page_code,
    )

    for region in existing_regions:
        if region.region_type == template_region.template_region_code:
            return region

    def exists(candidate: str) -> bool:
        return any(region.region_code == candidate for region in existing_regions)

    region = SiteBuilderRegion(
        site_code=context.site_code,
        surface_code=context.surface_code,
        page_code=context.page_code,
        region_code=next_region_code(
            context.page_code,
            template_region.template_region_code,
            exists,
        ),
        region_name=template_region.default_region_name,
        region_type=template_region.template_region_code,
        sort_order=template_region.sort_order,
        status="active",
    )

    add_region(session, region)
    session.flush()

    return region


def _validate_content(
    slot: BlockSlotCapability,
    content: dict[str, object],
) -> None:
    for field in slot.content_fields:
        if not field.required:
            continue

        value = content.get(field.field_key)

        if value is None:
            raise HTTPException(
                status_code=422,
                detail=f"missing_required_content_field:{field.field_key}",
            )

        if isinstance(value, str) and not value.strip():
            raise HTTPException(
                status_code=422,
                detail=f"missing_required_content_field:{field.field_key}",
            )
