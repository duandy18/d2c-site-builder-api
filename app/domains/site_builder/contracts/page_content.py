from pydantic import BaseModel, Field

from app.domains.site_builder.contracts.page_authoring_common import JsonRecord


class PageContentSlotDto(BaseModel):
    slot_code: str
    label: str
    description: str
    block_type: str
    renderer_key: str
    required: bool
    default_block_name: str
    sort_order: int
    content_schema: JsonRecord = Field(default_factory=dict)
    presentation_schema: JsonRecord = Field(default_factory=dict)
    default_content: JsonRecord = Field(default_factory=dict)
    default_presentation: JsonRecord = Field(default_factory=dict)
    validation: JsonRecord = Field(default_factory=dict)
    block_code: str | None = None
    status: str | None = None
    content: JsonRecord = Field(default_factory=dict)
    presentation: JsonRecord = Field(default_factory=dict)


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
    content: JsonRecord = Field(default_factory=dict)
    presentation: JsonRecord = Field(default_factory=dict)


class SlotContentResponse(BaseModel):
    slot_code: str
    block_code: str
    block_type: str
    renderer_key: str
    content: JsonRecord
    presentation: JsonRecord
    status: str
