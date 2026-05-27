from __future__ import annotations

from typing import Any

from app.domains.site_builder.contracts.page_authoring_common import TemplateBlockSlotDto
from app.domains.site_builder.contracts.template_catalog import (
    TemplateCatalogItemDto,
    TemplateCatalogRegionDto,
    TemplateCatalogResponse,
)
from app.domains.site_builder.services.page_authoring_capabilities import (
    TEMPLATE_BY_SURFACE_PAGE,
    content_field_to_dto,
    get_renderer_key,
    get_template_name,
    list_template_region_capabilities,
)

PAGE_TITLES = {
    "home": "首页",
    "category_entry": "分类入口页",
    "product_list": "商品列表页",
    "campaign": "活动页",
    "content_page": "内容页",
}


def _surface_route_slug(surface_code: str) -> str:
    return surface_code.replace("_", "-")


def _page_route_slug(page_code: str) -> str:
    return page_code.replace("_", "-")


def _route_path(surface_code: str, page_code: str) -> str:
    return f"/{_surface_route_slug(surface_code)}/{_page_route_slug(page_code)}"


def _field_count(slot: TemplateBlockSlotDto) -> int:
    total = 0

    for field in slot.content_fields:
        total += 1
        total += len(field.item_fields)

    return total


def _slot_to_dto(surface_code: str, slot: Any) -> TemplateBlockSlotDto:
    return TemplateBlockSlotDto(
        slot_code=slot.slot_code,
        label=slot.label,
        description=slot.description,
        block_type=slot.block_type,
        renderer_key=get_renderer_key(surface_code, slot.block_type),
        required=slot.required,
        default_block_name=slot.default_block_name,
        sort_order=slot.sort_order,
        content_fields=[content_field_to_dto(field) for field in slot.content_fields],
    )


def list_template_catalog() -> TemplateCatalogResponse:
    templates: list[TemplateCatalogItemDto] = []

    for surface_code, page_code in sorted(TEMPLATE_BY_SURFACE_PAGE):
        template_key = TEMPLATE_BY_SURFACE_PAGE[(surface_code, page_code)]
        source_regions = list_template_region_capabilities(template_key)

        regions: list[TemplateCatalogRegionDto] = []
        slot_count = 0
        field_count = 0

        for source_region in sorted(source_regions, key=lambda item: item.sort_order):
            slots = [
                _slot_to_dto(surface_code, slot)
                for slot in sorted(source_region.block_slots, key=lambda item: item.sort_order)
            ]

            slot_count += len(slots)
            field_count += sum(_field_count(slot) for slot in slots)

            regions.append(
                TemplateCatalogRegionDto(
                    template_region_code=source_region.template_region_code,
                    label=source_region.label,
                    description=source_region.description,
                    required=source_region.required,
                    default_region_name=source_region.default_region_name,
                    sort_order=source_region.sort_order,
                    slots=slots,
                )
            )

        templates.append(
            TemplateCatalogItemDto(
                template_key=template_key,
                template_name=get_template_name(template_key),
                surface_code=surface_code,
                page_code=page_code,
                page_title=PAGE_TITLES.get(page_code, page_code),
                route_path=_route_path(surface_code, page_code),
                region_count=len(regions),
                slot_count=slot_count,
                field_count=field_count,
                regions=regions,
            )
        )

    return TemplateCatalogResponse(templates=templates)
