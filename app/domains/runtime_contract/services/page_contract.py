from sqlalchemy.orm import Session

from app.domains.runtime_contract.contracts.page_contract import (
    RuntimeBlockContractDto,
    RuntimePageContractResponse,
    RuntimeRegionContractDto,
)
from app.domains.site_builder.contracts.page_content import (
    PageContentFormResponse,
    PageContentRegionGroupDto,
    PageContentSlotDto,
)
from app.domains.site_builder.services.page_content import build_page_content_form


def build_runtime_page_contract(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> RuntimePageContractResponse:
    form = build_page_content_form(session, site_code, surface_code, page_code)

    return RuntimePageContractResponse(
        site_code=form.site_code,
        surface_code=form.surface_code,
        page_code=form.page_code,
        page_title=form.page_title,
        template_key=form.template_key,
        template_name=form.template_name,
        regions=[_region_to_runtime(form, group) for group in form.groups],
    )


def _region_to_runtime(
    form: PageContentFormResponse,
    group: PageContentRegionGroupDto,
) -> RuntimeRegionContractDto:
    blocks = [_slot_to_runtime(form, slot) for slot in group.slots]
    has_active_block = any(block.status == "active" for block in blocks)

    return RuntimeRegionContractDto(
        template_region_code=group.template_region_code,
        region_code=f"{form.page_code}.{group.template_region_code}",
        region_name=group.default_region_name,
        required=group.required,
        sort_order=group.sort_order,
        status="active" if has_active_block else "empty",
        blocks=blocks,
    )


def _slot_to_runtime(
    form: PageContentFormResponse,
    slot: PageContentSlotDto,
) -> RuntimeBlockContractDto:
    is_filled = slot.status == "active" and bool(slot.content)
    block_code = slot.block_code or f"{form.page_code}.{slot.slot_code}"

    return RuntimeBlockContractDto(
        slot_code=slot.slot_code,
        block_code=block_code,
        block_type=slot.block_type,
        renderer_key=slot.renderer_key,
        required=slot.required,
        sort_order=slot.sort_order,
        status=slot.status if slot.status in {"active", "disabled"} else "empty",
        is_filled=is_filled,
        content=dict(slot.content or {}),
        presentation=dict(slot.presentation or {}),
    )
