from typing import Any

from pydantic import BaseModel, Field

JsonRecord = dict[str, Any]


class OptionItem(BaseModel):
    value: str
    label: str
    description: str


class ContentFieldDto(BaseModel):
    field_key: str
    label: str
    field_type: str
    value_type: str
    editor_type: str
    required: bool
    placeholder: str | None = None
    help_text: str | None = None
    options: list[OptionItem] = Field(default_factory=list)
    item_fields: list["ContentFieldDto"] = Field(default_factory=list)


class TemplateBlockSlotDto(BaseModel):
    slot_code: str
    label: str
    description: str
    block_type: str
    renderer_key: str
    required: bool
    default_block_name: str
    sort_order: int
    content_fields: list[ContentFieldDto]


class PageAuthoringBlockDto(BaseModel):
    block_code: str
    block_name: str
    block_type: str
    renderer_key: str
    sort_order: int
    content: JsonRecord
    layout: JsonRecord
    status: str


class PageAuthoringRegionDto(BaseModel):
    region_code: str
    region_name: str
    region_type: str
    template_region_code: str
    sort_order: int
    status: str
    blocks: list[PageAuthoringBlockDto] = Field(default_factory=list)


ContentFieldDto.model_rebuild()
