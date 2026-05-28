from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domains.site_builder.contracts.page_authoring_common import (
    OptionItem,
    TemplateBlockSlotDto,
)
from app.domains.site_builder.contracts.page_planner import (
    RegionBlockRule,
    TemplateRegionOption,
)
from app.domains.site_builder.models.pc_home import (
    SiteBuilderTemplateRegion,
    SiteBuilderTemplateSlot,
)
from app.domains.site_builder.repos.templates import (
    get_template,
    get_template_slot,
    list_template_regions,
    list_template_slots,
    list_template_slots_for_region,
)

PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY = "pc_home_simple_shop_v1"
PC_PRODUCT_DETAIL_GALLERY_TEMPLATE_KEY = "pc_product_detail_gallery_v1"
PC_PRODUCT_DETAIL_IMAGE_MATRIX_TEMPLATE_KEY = "pc_product_detail_image_matrix_v1"


def require_template_name(session: Session, template_key: str) -> str:
    template = get_template(session, template_key)

    if template is None:
        raise HTTPException(status_code=422, detail="unsupported_page_template")

    return template.template_name


def template_slot_to_dto(slot: SiteBuilderTemplateSlot) -> TemplateBlockSlotDto:
    return TemplateBlockSlotDto(
        slot_code=slot.slot_code,
        label=slot.label,
        description=slot.description,
        block_type=slot.block_type,
        renderer_key=slot.renderer_key,
        required=slot.required,
        default_block_name=slot.default_block_name,
        sort_order=slot.sort_order,
        content_schema=dict(slot.content_schema_json or {}),
        presentation_schema=dict(slot.presentation_schema_json or {}),
        default_content=dict(slot.default_content_json or {}),
        default_presentation=dict(slot.default_presentation_json or {}),
        validation=dict(slot.validation_json or {}),
    )


def list_template_region_options(
    session: Session,
    template_key: str,
) -> list[TemplateRegionOption]:
    regions = list_template_regions(session, template_key)

    if not regions and get_template(session, template_key) is None:
        raise HTTPException(status_code=422, detail="unsupported_page_template")

    return [
        TemplateRegionOption(
            template_region_code=region.template_region_code,
            label=region.label,
            description=region.description,
            required=region.required,
            default_region_name=region.default_region_name,
            sort_order=region.sort_order,
            allowed_block_types=sorted(
                {
                    slot.block_type
                    for slot in list_template_slots_for_region(
                        session,
                        template_key,
                        region.template_region_code,
                    )
                }
            ),
            block_slots=[
                template_slot_to_dto(slot)
                for slot in list_template_slots_for_region(
                    session,
                    template_key,
                    region.template_region_code,
                )
            ],
        )
        for region in regions
    ]


def list_region_options(session: Session, template_key: str) -> list[OptionItem]:
    return [
        OptionItem(
            value=region.template_region_code,
            label=region.label,
            description=region.description,
        )
        for region in list_template_regions(session, template_key)
    ]


def list_block_options(session: Session) -> list[OptionItem]:
    seen: dict[str, OptionItem] = {}

    for template in (
        "pc_home_simple_shop_v1",
        "pc_product_detail_gallery_v1",
        "pc_product_detail_image_matrix_v1",
    ):
        for slot in list_template_slots(session, template):
            seen.setdefault(
                slot.block_type,
                OptionItem(
                    value=slot.block_type,
                    label=slot.label,
                    description=slot.description,
                ),
            )

    return sorted(seen.values(), key=lambda item: item.value)


def list_region_block_rules(session: Session, template_key: str) -> list[RegionBlockRule]:
    return [
        RegionBlockRule(
            region_type=region.template_region_code,
            template_region_code=region.template_region_code,
            allowed_block_types=sorted(
                {
                    slot.block_type
                    for slot in list_template_slots_for_region(
                        session,
                        template_key,
                        region.template_region_code,
                    )
                }
            ),
        )
        for region in list_template_regions(session, template_key)
    ]


def require_template_region(
    session: Session,
    template_key: str,
    template_region_code: str,
) -> SiteBuilderTemplateRegion:
    for region in list_template_regions(session, template_key):
        if region.template_region_code == template_region_code:
            return region

    raise HTTPException(status_code=422, detail="unsupported_template_region")


def require_block_slot(
    session: Session,
    template_key: str,
    slot_code: str,
) -> tuple[SiteBuilderTemplateRegion, SiteBuilderTemplateSlot]:
    slot = get_template_slot(session, template_key, slot_code)

    if slot is None:
        raise HTTPException(status_code=422, detail="unsupported_block_slot")

    region = require_template_region(session, template_key, slot.template_region_code)

    return region, slot


def require_block_type_allowed(
    session: Session,
    template_key: str,
    template_region_code: str,
    block_type: str,
) -> str:
    for slot in list_template_slots_for_region(session, template_key, template_region_code):
        if slot.block_type == block_type:
            return slot.renderer_key

    raise HTTPException(status_code=422, detail="block_type_not_allowed_for_region")
