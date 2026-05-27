import re
from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domains.site_builder.contracts.pc_home import (
    CreateBlockRequest,
    CreateRegionRequest,
    OptionItem,
    PcHomeBlockDto,
    PcHomeDraftResponse,
    PcHomePlannerOptionsResponse,
    PcHomeRegionDto,
    UpdateBlockRequest,
    UpdateRegionRequest,
)
from app.domains.site_builder.models.pc_home import SiteBuilderBlock, SiteBuilderRegion
from app.domains.site_builder.repos.pc_home import (
    add_block,
    add_region,
    get_block,
    get_page,
    get_region,
    list_blocks,
    list_regions,
)

DEFAULT_SITE_CODE = "default"
PC_WEB_SURFACE_CODE = "pc_web"
HOME_PAGE_CODE = "home"

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

RENDERER_BY_BLOCK_TYPE = {
    "title": "pc_web.title",
    "hero_banner": "pc_web.hero_banner",
    "offer_shelf": "pc_web.offer_shelf_grid",
    "promotion_strip": "pc_web.promotion_strip",
    "rich_text": "pc_web.rich_text",
}


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")

    return normalized or "item"


def _require_home_page(session: Session) -> str:
    page = get_page(session, DEFAULT_SITE_CODE, PC_WEB_SURFACE_CODE, HOME_PAGE_CODE)

    if not page:
        raise HTTPException(status_code=404, detail="pc_home_page_not_found")

    return page.page_title


def get_planner_options() -> PcHomePlannerOptionsResponse:
    return PcHomePlannerOptionsResponse(
        allowed_region_types=REGION_OPTIONS,
        allowed_block_types=BLOCK_OPTIONS,
    )


def build_home_draft(session: Session) -> PcHomeDraftResponse:
    page_title = _require_home_page(session)
    regions = list_regions(session, DEFAULT_SITE_CODE, PC_WEB_SURFACE_CODE, HOME_PAGE_CODE)
    blocks = list_blocks(session, DEFAULT_SITE_CODE, PC_WEB_SURFACE_CODE, HOME_PAGE_CODE)

    blocks_by_region: dict[str, list[SiteBuilderBlock]] = defaultdict(list)
    for block in blocks:
        blocks_by_region[block.region_code].append(block)

    region_dtos = [
        PcHomeRegionDto(
            region_code=region.region_code,
            region_name=region.region_name,
            region_type=region.region_type,
            sort_order=region.sort_order,
            status=region.status,
            blocks=[
                PcHomeBlockDto(
                    block_code=block.block_code,
                    block_name=block.block_name,
                    block_type=block.block_type,
                    renderer_key=block.renderer_key,
                    sort_order=block.sort_order,
                    content=dict(block.content_json or {}),
                    layout=dict(block.layout_json or {}),
                    status=block.status,
                )
                for block in blocks_by_region[region.region_code]
            ],
        )
        for region in regions
    ]

    return PcHomeDraftResponse(
        site_code=DEFAULT_SITE_CODE,
        surface_code=PC_WEB_SURFACE_CODE,
        page_code=HOME_PAGE_CODE,
        page_title=page_title,
        regions=region_dtos,
    )


def create_region(session: Session, request: CreateRegionRequest) -> PcHomeRegionDto:
    _require_home_page(session)

    base_code = f"home.{request.region_type}"
    region_code = base_code
    suffix = 2

    while get_region(session, DEFAULT_SITE_CODE, PC_WEB_SURFACE_CODE, HOME_PAGE_CODE, region_code):
        region_code = f"{base_code}-{suffix}"
        suffix += 1

    region = SiteBuilderRegion(
        site_code=DEFAULT_SITE_CODE,
        surface_code=PC_WEB_SURFACE_CODE,
        page_code=HOME_PAGE_CODE,
        region_code=region_code,
        region_name=request.region_name,
        region_type=request.region_type,
        sort_order=request.sort_order,
        status="active",
    )

    add_region(session, region)
    session.commit()
    session.refresh(region)

    return PcHomeRegionDto(
        region_code=region.region_code,
        region_name=region.region_name,
        region_type=region.region_type,
        sort_order=region.sort_order,
        status=region.status,
        blocks=[],
    )


def update_region(
    session: Session,
    region_code: str,
    request: UpdateRegionRequest,
) -> PcHomeRegionDto:
    region = get_region(
        session,
        DEFAULT_SITE_CODE,
        PC_WEB_SURFACE_CODE,
        HOME_PAGE_CODE,
        region_code,
    )

    if not region:
        raise HTTPException(status_code=404, detail="region_not_found")

    if request.region_name is not None:
        region.region_name = request.region_name

    if request.sort_order is not None:
        region.sort_order = request.sort_order

    if request.status is not None:
        region.status = request.status

    session.commit()
    session.refresh(region)

    return PcHomeRegionDto(
        region_code=region.region_code,
        region_name=region.region_name,
        region_type=region.region_type,
        sort_order=region.sort_order,
        status=region.status,
        blocks=[],
    )


def create_block(
    session: Session,
    region_code: str,
    request: CreateBlockRequest,
) -> PcHomeBlockDto:
    region = get_region(
        session,
        DEFAULT_SITE_CODE,
        PC_WEB_SURFACE_CODE,
        HOME_PAGE_CODE,
        region_code,
    )

    if not region:
        raise HTTPException(status_code=404, detail="region_not_found")

    renderer_key = RENDERER_BY_BLOCK_TYPE[request.block_type]
    base_code = f"{region_code}.{_slugify(request.block_type)}"
    block_code = base_code
    suffix = 2

    while get_block(session, DEFAULT_SITE_CODE, PC_WEB_SURFACE_CODE, HOME_PAGE_CODE, block_code):
        block_code = f"{base_code}-{suffix}"
        suffix += 1

    block = SiteBuilderBlock(
        site_code=DEFAULT_SITE_CODE,
        surface_code=PC_WEB_SURFACE_CODE,
        page_code=HOME_PAGE_CODE,
        region_code=region_code,
        block_code=block_code,
        block_name=request.block_name,
        block_type=request.block_type,
        renderer_key=renderer_key,
        sort_order=request.sort_order,
        content_json=request.content,
        layout_json=request.layout,
        status="active",
    )

    add_block(session, block)
    session.commit()
    session.refresh(block)

    return _block_to_dto(block)


def update_block(
    session: Session,
    block_code: str,
    request: UpdateBlockRequest,
) -> PcHomeBlockDto:
    block = get_block(session, DEFAULT_SITE_CODE, PC_WEB_SURFACE_CODE, HOME_PAGE_CODE, block_code)

    if not block:
        raise HTTPException(status_code=404, detail="block_not_found")

    if request.block_name is not None:
        block.block_name = request.block_name

    if request.sort_order is not None:
        block.sort_order = request.sort_order

    if request.content is not None:
        block.content_json = request.content

    if request.layout is not None:
        block.layout_json = request.layout

    if request.status is not None:
        block.status = request.status

    session.commit()
    session.refresh(block)

    return _block_to_dto(block)


def _block_to_dto(block: SiteBuilderBlock) -> PcHomeBlockDto:
    return PcHomeBlockDto(
        block_code=block.block_code,
        block_name=block.block_name,
        block_type=block.block_type,
        renderer_key=block.renderer_key,
        sort_order=block.sort_order,
        content=dict(block.content_json or {}),
        layout=dict(block.layout_json or {}),
        status=block.status,
    )
