from sqlalchemy.orm import Session

from app.domains.site_builder.contracts.template_catalog import (
    TemplateCatalogItemDto,
    TemplateCatalogRegionDto,
    TemplateCatalogResponse,
)
from app.domains.site_builder.repos.templates import (
    list_template_regions,
    list_template_slots_for_region,
    list_templates,
)
from app.domains.site_builder.services.page_authoring_capabilities import template_slot_to_dto


def _surface_route_slug(surface_code: str) -> str:
    return surface_code.replace("_", "-")


def _page_route_slug(page_code: str) -> str:
    return page_code.replace("_", "-")


def _route_path(surface_code: str, page_code: str) -> str:
    return f"/{_surface_route_slug(surface_code)}/{_page_route_slug(page_code)}"


def _field_count(content_schema: dict[str, object]) -> int:
    fields = content_schema.get("fields")

    if isinstance(fields, dict):
        return len(fields)

    return 0


def list_template_catalog(session: Session) -> TemplateCatalogResponse:
    templates: list[TemplateCatalogItemDto] = []

    for template in list_templates(session):
        regions: list[TemplateCatalogRegionDto] = []
        slot_count = 0
        field_count = 0

        for source_region in list_template_regions(session, template.template_key):
            slots = [
                template_slot_to_dto(slot)
                for slot in list_template_slots_for_region(
                    session,
                    template.template_key,
                    source_region.template_region_code,
                )
            ]

            slot_count += len(slots)
            field_count += sum(_field_count(slot.content_schema) for slot in slots)

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
                template_key=template.template_key,
                template_name=template.template_name,
                surface_code=template.surface_code,
                page_code=template.page_code,
                page_title=template.template_name,
                route_path=_route_path(template.surface_code, template.page_code),
                region_count=len(regions),
                slot_count=slot_count,
                field_count=field_count,
                regions=regions,
            )
        )

    return TemplateCatalogResponse(templates=templates)
