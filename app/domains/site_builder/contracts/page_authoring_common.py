from typing import Any

from pydantic import BaseModel, Field

JsonRecord = dict[str, Any]


class OptionItem(BaseModel):
    value: str
    label: str
    description: str


class TemplateBlockSlotDto(BaseModel):
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


class PageAuthoringBlockDto(BaseModel):
    block_code: str
    block_name: str
    block_type: str
    renderer_key: str
    sort_order: int
    content: JsonRecord
    presentation: JsonRecord
    status: str


class PageAuthoringRegionDto(BaseModel):
    region_code: str
    region_name: str
    region_type: str
    template_region_code: str
    sort_order: int
    status: str
    blocks: list[PageAuthoringBlockDto] = Field(default_factory=list)
