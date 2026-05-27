from pydantic import BaseModel

from app.domains.site_builder.contracts.page_authoring_common import (
    ContentFieldDto,
    JsonRecord,
)


class PageContentSlotDto(BaseModel):
    slot_code: str
    label: str
    description: str
    block_type: str
    renderer_key: str
    required: bool
    default_block_name: str
    sort_order: int
    content_fields: list[ContentFieldDto]
    block_code: str | None = None
    status: str | None = None
    content: JsonRecord


class PageContentRegionGroupDto(BaseModel):
    template_region_code: str
    label: str
    description: str
    required: bool
    default_region_name: str
    sort_order: int
    slots: list[PageContentSlotDto]


class PageContentFormResponse(BaseModel):
    site_code: str
    surface_code: str
    page_code: str
    page_title: str
    template_key: str
    template_name: str
    groups: list[PageContentRegionGroupDto]


class UpdateSlotContentRequest(BaseModel):
    content: JsonRecord


class SlotContentResponse(BaseModel):
    slot_code: str
    block_code: str
    block_type: str
    renderer_key: str
    content: JsonRecord
    status: str
