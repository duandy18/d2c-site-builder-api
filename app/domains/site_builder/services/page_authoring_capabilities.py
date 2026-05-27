from fastapi import HTTPException

from app.domains.site_builder.contracts.page_authoring_common import OptionItem
from app.domains.site_builder.contracts.page_planner import RegionBlockRule

REGION_OPTIONS = [
    OptionItem(value="hero", label="头图区域", description="首页顶部主视觉区域"),
    OptionItem(value="navigation", label="导航入口", description="分类或频道入口区域"),
    OptionItem(value="main", label="主体内容", description="首页主体内容区域"),
    OptionItem(value="recommendation", label="推荐区域", description="推荐商品或内容区域"),
]

BLOCK_OPTIONS = [
    OptionItem(value="title", label="标题", description="区域标题或说明"),
    OptionItem(value="hero_banner", label="广告位", description="首页主广告或活动 Banner"),
    OptionItem(value="offer_shelf", label="商品货架", description="展示一组上架商品"),
    OptionItem(value="promotion_strip", label="促销条", description="展示促销或优惠信息"),
    OptionItem(value="rich_text", label="图文内容", description="展示富文本或说明内容"),
]

REGION_BLOCK_RULES: dict[str, list[str]] = {
    "hero": ["title", "hero_banner", "promotion_strip"],
    "navigation": ["title", "rich_text"],
    "main": ["title", "offer_shelf", "promotion_strip", "rich_text"],
    "recommendation": ["title", "offer_shelf"],
}

RENDERER_BY_SURFACE_AND_BLOCK_TYPE: dict[str, dict[str, str]] = {
    "pc_web": {
        "title": "pc_web.title",
        "hero_banner": "pc_web.hero_banner",
        "offer_shelf": "pc_web.offer_shelf_grid",
        "promotion_strip": "pc_web.promotion_strip",
        "rich_text": "pc_web.rich_text",
    }
}


def list_region_options() -> list[OptionItem]:
    return REGION_OPTIONS


def list_block_options() -> list[OptionItem]:
    return BLOCK_OPTIONS


def list_region_block_rules() -> list[RegionBlockRule]:
    return [
        RegionBlockRule(region_type=region_type, allowed_block_types=block_types)
        for region_type, block_types in REGION_BLOCK_RULES.items()
    ]


def require_region_type(region_type: str) -> str:
    allowed_region_types = {item.value for item in REGION_OPTIONS}

    if region_type not in allowed_region_types:
        raise HTTPException(status_code=422, detail="unsupported_region_type")

    return region_type


def require_block_type_allowed(
    surface_code: str,
    region_type: str,
    block_type: str,
) -> str:
    allowed_block_types = REGION_BLOCK_RULES.get(region_type, [])

    if block_type not in allowed_block_types:
        raise HTTPException(status_code=422, detail="block_type_not_allowed_for_region")

    renderer_map = RENDERER_BY_SURFACE_AND_BLOCK_TYPE.get(surface_code, {})
    renderer_key = renderer_map.get(block_type)

    if not renderer_key:
        raise HTTPException(status_code=422, detail="unsupported_block_renderer")

    return renderer_key
