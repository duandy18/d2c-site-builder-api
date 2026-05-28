from typing import Any, Literal

from pydantic import BaseModel, Field

JsonRecord = dict[str, Any]


class RuntimeBlockContractDto(BaseModel):
    slot_code: str
    block_code: str
    block_type: str
    renderer_key: str
    required: bool
    sort_order: int
    status: Literal["active", "empty", "disabled"]
    is_filled: bool
    content: JsonRecord = Field(default_factory=dict)
    presentation: JsonRecord = Field(default_factory=dict)


class RuntimeRegionContractDto(BaseModel):
    template_region_code: str
    region_code: str
    region_name: str
    required: bool
    sort_order: int
    status: Literal["active", "empty", "disabled"]
    blocks: list[RuntimeBlockContractDto] = Field(default_factory=list)


class RuntimePageContractResponse(BaseModel):
    contract_type: Literal["site_builder.page"] = "site_builder.page"
    contract_version: str = "draft-preview-v1"
    site_code: str
    surface_code: str
    page_code: str
    page_title: str
    template_key: str
    template_name: str
    status: Literal["draft_preview"] = "draft_preview"
    regions: list[RuntimeRegionContractDto] = Field(default_factory=list)
