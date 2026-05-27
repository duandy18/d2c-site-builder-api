from pydantic import BaseModel, Field

from app.domains.site_builder.contracts.page_authoring_common import TemplateBlockSlotDto


class TemplateCatalogRegionDto(BaseModel):
    template_region_code: str
    label: str
    description: str
    required: bool
    default_region_name: str
    sort_order: int
    slots: list[TemplateBlockSlotDto] = Field(default_factory=list)


class TemplateCatalogItemDto(BaseModel):
    template_key: str
    template_name: str
    surface_code: str
    page_code: str
    page_title: str
    route_path: str
    region_count: int
    slot_count: int
    field_count: int
    regions: list[TemplateCatalogRegionDto] = Field(default_factory=list)


class TemplateCatalogResponse(BaseModel):
    templates: list[TemplateCatalogItemDto] = Field(default_factory=list)
