from pydantic import BaseModel

from app.domains.site_builder.contracts.page_authoring_common import OptionItem


class TemplateRegionOption(BaseModel):
    template_region_code: str
    label: str
    description: str
    required: bool
    default_region_name: str
    sort_order: int
    allowed_block_types: list[str]


class RegionBlockRule(BaseModel):
    region_type: str
    template_region_code: str
    allowed_block_types: list[str]


class PagePlannerOptionsResponse(BaseModel):
    template_key: str
    template_name: str
    template_regions: list[TemplateRegionOption]
    allowed_region_types: list[OptionItem]
    allowed_block_types: list[OptionItem]
    region_block_rules: list[RegionBlockRule]
