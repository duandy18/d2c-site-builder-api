from pydantic import BaseModel

from app.domains.site_builder.contracts.page_authoring_common import OptionItem


class RegionBlockRule(BaseModel):
    region_type: str
    allowed_block_types: list[str]


class PagePlannerOptionsResponse(BaseModel):
    allowed_region_types: list[OptionItem]
    allowed_block_types: list[OptionItem]
    region_block_rules: list[RegionBlockRule]
