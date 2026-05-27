from typing import Any, Literal

from pydantic import BaseModel, Field

RegionType = Literal["hero", "navigation", "main", "recommendation"]
BlockType = Literal["title", "hero_banner", "offer_shelf", "promotion_strip", "rich_text"]


class OptionItem(BaseModel):
    value: str
    label: str
    description: str


class PcHomePlannerOptionsResponse(BaseModel):
    allowed_region_types: list[OptionItem]
    allowed_block_types: list[OptionItem]


class PcHomeBlockDto(BaseModel):
    block_code: str
    block_name: str
    block_type: str
    renderer_key: str
    sort_order: int
    content: dict[str, Any]
    layout: dict[str, Any]
    status: str


class PcHomeRegionDto(BaseModel):
    region_code: str
    region_name: str
    region_type: str
    sort_order: int
    status: str
    blocks: list[PcHomeBlockDto] = Field(default_factory=list)


class PcHomeDraftResponse(BaseModel):
    site_code: str
    surface_code: str
    page_code: str
    page_title: str
    regions: list[PcHomeRegionDto]


class CreateRegionRequest(BaseModel):
    region_name: str
    region_type: RegionType
    sort_order: int = 100


class UpdateRegionRequest(BaseModel):
    region_name: str | None = None
    sort_order: int | None = None
    status: Literal["active", "disabled"] | None = None


class CreateBlockRequest(BaseModel):
    block_name: str
    block_type: BlockType
    sort_order: int = 100
    content: dict[str, Any] = Field(default_factory=dict)
    layout: dict[str, Any] = Field(default_factory=dict)


class UpdateBlockRequest(BaseModel):
    block_name: str | None = None
    sort_order: int | None = None
    content: dict[str, Any] | None = None
    layout: dict[str, Any] | None = None
    status: Literal["active", "disabled"] | None = None
