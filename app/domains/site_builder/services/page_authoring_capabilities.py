from dataclasses import dataclass

from fastapi import HTTPException

from app.domains.site_builder.contracts.page_authoring_common import OptionItem
from app.domains.site_builder.contracts.page_planner import (
    RegionBlockRule,
    TemplateRegionOption,
)

PC_HOME_STANDARD_TEMPLATE_KEY = "pc_home_standard_v1"
PC_HOME_STANDARD_TEMPLATE_NAME = "标准电商首页"


@dataclass(frozen=True)
class BlockCapability:
    block_type: str
    label: str
    description: str
    renderer_by_surface: dict[str, str]


@dataclass(frozen=True)
class TemplateRegionCapability:
    template_region_code: str
    label: str
    description: str
    required: bool
    default_region_name: str
    sort_order: int
    allowed_block_types: list[str]


BLOCK_CAPABILITIES = [
    BlockCapability(
        block_type="title",
        label="标题",
        description="区域标题或说明",
        renderer_by_surface={"pc_web": "pc_web.title"},
    ),
    BlockCapability(
        block_type="hero_banner",
        label="广告位",
        description="广告图、活动图或首屏视觉",
        renderer_by_surface={"pc_web": "pc_web.hero_banner"},
    ),
    BlockCapability(
        block_type="entry_grid",
        label="入口宫格",
        description="分类入口、频道入口或快捷入口",
        renderer_by_surface={"pc_web": "pc_web.entry_grid"},
    ),
    BlockCapability(
        block_type="offer_shelf",
        label="商品货架",
        description="展示一组商品",
        renderer_by_surface={"pc_web": "pc_web.offer_shelf_grid"},
    ),
    BlockCapability(
        block_type="promotion_strip",
        label="促销条",
        description="展示优惠或促销信息",
        renderer_by_surface={"pc_web": "pc_web.promotion_strip"},
    ),
    BlockCapability(
        block_type="rich_text",
        label="图文内容",
        description="品牌介绍、说明文本或富文本",
        renderer_by_surface={"pc_web": "pc_web.rich_text"},
    ),
]

PC_HOME_STANDARD_REGIONS = [
    TemplateRegionCapability(
        template_region_code="hero",
        label="首屏区",
        description="首页顶部主视觉区域，可放标题、广告图和促销条",
        required=True,
        default_region_name="首页首屏",
        sort_order=10,
        allowed_block_types=["title", "hero_banner", "promotion_strip"],
    ),
    TemplateRegionCapability(
        template_region_code="entry",
        label="入口区",
        description="分类入口、频道入口或活动入口",
        required=False,
        default_region_name="快捷入口",
        sort_order=20,
        allowed_block_types=["title", "entry_grid", "rich_text"],
    ),
    TemplateRegionCapability(
        template_region_code="product_showcase",
        label="商品展示区",
        description="热卖、新品、推荐或促销商品货架",
        required=True,
        default_region_name="商品展示",
        sort_order=30,
        allowed_block_types=["title", "offer_shelf", "promotion_strip"],
    ),
    TemplateRegionCapability(
        template_region_code="content",
        label="内容营销区",
        description="品牌故事、活动说明或图文内容",
        required=False,
        default_region_name="内容营销",
        sort_order=40,
        allowed_block_types=["title", "rich_text", "hero_banner"],
    ),
    TemplateRegionCapability(
        template_region_code="footer_promo",
        label="底部推荐区",
        description="底部推荐商品、补充说明或收尾营销",
        required=False,
        default_region_name="底部推荐",
        sort_order=50,
        allowed_block_types=["title", "offer_shelf", "rich_text", "promotion_strip"],
    ),
]


def get_template_key(surface_code: str, page_code: str) -> str:
    if surface_code == "pc_web" and page_code == "home":
        return PC_HOME_STANDARD_TEMPLATE_KEY

    raise HTTPException(status_code=422, detail="unsupported_page_template")


def get_template_name(template_key: str) -> str:
    if template_key == PC_HOME_STANDARD_TEMPLATE_KEY:
        return PC_HOME_STANDARD_TEMPLATE_NAME

    raise HTTPException(status_code=422, detail="unsupported_page_template")


def list_template_region_capabilities(
    template_key: str,
) -> list[TemplateRegionCapability]:
    if template_key == PC_HOME_STANDARD_TEMPLATE_KEY:
        return PC_HOME_STANDARD_REGIONS

    raise HTTPException(status_code=422, detail="unsupported_page_template")


def list_template_region_options(template_key: str) -> list[TemplateRegionOption]:
    return [
        TemplateRegionOption(
            template_region_code=item.template_region_code,
            label=item.label,
            description=item.description,
            required=item.required,
            default_region_name=item.default_region_name,
            sort_order=item.sort_order,
            allowed_block_types=item.allowed_block_types,
        )
        for item in list_template_region_capabilities(template_key)
    ]


def list_region_options(template_key: str) -> list[OptionItem]:
    return [
        OptionItem(
            value=item.template_region_code,
            label=item.label,
            description=item.description,
        )
        for item in list_template_region_capabilities(template_key)
    ]


def list_block_options() -> list[OptionItem]:
    return [
        OptionItem(
            value=item.block_type,
            label=item.label,
            description=item.description,
        )
        for item in BLOCK_CAPABILITIES
    ]


def list_region_block_rules(template_key: str) -> list[RegionBlockRule]:
    return [
        RegionBlockRule(
            region_type=item.template_region_code,
            template_region_code=item.template_region_code,
            allowed_block_types=item.allowed_block_types,
        )
        for item in list_template_region_capabilities(template_key)
    ]


def require_template_region(
    template_key: str,
    template_region_code: str,
) -> TemplateRegionCapability:
    for item in list_template_region_capabilities(template_key):
        if item.template_region_code == template_region_code:
            return item

    raise HTTPException(status_code=422, detail="unsupported_template_region")


def require_block_type_allowed(
    surface_code: str,
    template_key: str,
    template_region_code: str,
    block_type: str,
) -> str:
    template_region = require_template_region(template_key, template_region_code)

    if block_type not in template_region.allowed_block_types:
        raise HTTPException(status_code=422, detail="block_type_not_allowed_for_region")

    for item in BLOCK_CAPABILITIES:
        if item.block_type == block_type:
            renderer_key = item.renderer_by_surface.get(surface_code)

            if renderer_key:
                return renderer_key

    raise HTTPException(status_code=422, detail="unsupported_block_renderer")
