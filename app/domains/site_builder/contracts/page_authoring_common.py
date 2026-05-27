from typing import Any

from pydantic import BaseModel, Field

JsonRecord = dict[str, Any]


class OptionItem(BaseModel):
    value: str
    label: str
    description: str


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
