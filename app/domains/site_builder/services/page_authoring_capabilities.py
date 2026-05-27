from dataclasses import dataclass

from fastapi import HTTPException

from app.domains.site_builder.contracts.page_authoring_common import (
    ContentFieldDto,
    OptionItem,
    TemplateBlockSlotDto,
)
from app.domains.site_builder.contracts.page_planner import (
    RegionBlockRule,
    TemplateRegionOption,
)

PC_HOME_STANDARD_TEMPLATE_KEY = "pc_home_standard_v1"
PC_HOME_STANDARD_TEMPLATE_NAME = "标准电商首页"


@dataclass(frozen=True)
class ContentFieldCapability:
    field_key: str
    label: str
    field_type: str
    required: bool
    placeholder: str | None = None
    help_text: str | None = None


@dataclass(frozen=True)
class BlockCapability:
    block_type: str
    label: str
    description: str
    renderer_by_surface: dict[str, str]


@dataclass(frozen=True)
class BlockSlotCapability:
    slot_code: str
    label: str
    description: str
    block_type: str
    required: bool
    default_block_name: str
    sort_order: int
    content_fields: list[ContentFieldCapability]


@dataclass(frozen=True)
class TemplateRegionCapability:
    template_region_code: str
    label: str
    description: str
    required: bool
    default_region_name: str
    sort_order: int
    block_slots: list[BlockSlotCapability]

    @property
    def allowed_block_types(self) -> list[str]:
        return sorted({slot.block_type for slot in self.block_slots})


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
        description="首页顶部主视觉区域",
        required=True,
        default_region_name="首页首屏",
        sort_order=10,
        block_slots=[
            BlockSlotCapability(
                slot_code="hero.title",
                label="首屏标题",
                description="首屏主标题和副标题",
                block_type="title",
                required=False,
                default_block_name="首屏标题",
                sort_order=10,
                content_fields=[
                    ContentFieldCapability(
                        field_key="title",
                        label="标题",
                        field_type="text",
                        required=True,
                        placeholder="五月宠物用品大促",
                    ),
                    ContentFieldCapability(
                        field_key="subtitle",
                        label="副标题",
                        field_type="text",
                        required=False,
                        placeholder="猫砂猫粮限时优惠",
                    ),
                ],
            ),
            BlockSlotCapability(
                slot_code="hero.banner",
                label="首屏广告",
                description="首屏广告图和跳转链接",
                block_type="hero_banner",
                required=True,
                default_block_name="首屏广告",
                sort_order=20,
                content_fields=[
                    ContentFieldCapability(
                        field_key="image_url",
                        label="广告图片",
                        field_type="image_url",
                        required=True,
                        placeholder="https://example.com/banner.jpg",
                    ),
                    ContentFieldCapability(
                        field_key="link_url",
                        label="跳转链接",
                        field_type="url",
                        required=False,
                        placeholder="/campaign/may",
                    ),
                    ContentFieldCapability(
                        field_key="title",
                        label="图片标题",
                        field_type="text",
                        required=False,
                    ),
                ],
            ),
            BlockSlotCapability(
                slot_code="hero.promotion",
                label="首屏促销条",
                description="首屏下方促销提示",
                block_type="promotion_strip",
                required=False,
                default_block_name="首屏促销条",
                sort_order=30,
                content_fields=[
                    ContentFieldCapability(
                        field_key="text",
                        label="促销文案",
                        field_type="text",
                        required=True,
                        placeholder="满 99 减 20",
                    ),
                    ContentFieldCapability(
                        field_key="link_url",
                        label="跳转链接",
                        field_type="url",
                        required=False,
                    ),
                ],
            ),
        ],
    ),
    TemplateRegionCapability(
        template_region_code="entry",
        label="入口区",
        description="分类入口、频道入口或活动入口",
        required=False,
        default_region_name="快捷入口",
        sort_order=20,
        block_slots=[
            BlockSlotCapability(
                slot_code="entry.grid",
                label="入口宫格",
                description="首页快捷入口配置",
                block_type="entry_grid",
                required=False,
                default_block_name="快捷入口",
                sort_order=10,
                content_fields=[
                    ContentFieldCapability(
                        field_key="items",
                        label="入口列表",
                        field_type="json",
                        required=True,
                        placeholder='[{"title":"猫砂","link_url":"/c/cat-litter"}]',
                    )
                ],
            )
        ],
    ),
    TemplateRegionCapability(
        template_region_code="product_showcase",
        label="商品展示区",
        description="热卖、新品、推荐或促销商品货架",
        required=True,
        default_region_name="商品展示",
        sort_order=30,
        block_slots=[
            BlockSlotCapability(
                slot_code="product_showcase.title",
                label="商品展示标题",
                description="商品展示区标题",
                block_type="title",
                required=False,
                default_block_name="商品展示标题",
                sort_order=10,
                content_fields=[
                    ContentFieldCapability(
                        field_key="title",
                        label="标题",
                        field_type="text",
                        required=True,
                        placeholder="热卖商品",
                    )
                ],
            ),
            BlockSlotCapability(
                slot_code="product_showcase.shelf",
                label="商品货架",
                description="商品货架数据源",
                block_type="offer_shelf",
                required=True,
                default_block_name="商品货架",
                sort_order=20,
                content_fields=[
                    ContentFieldCapability(
                        field_key="title",
                        label="货架标题",
                        field_type="text",
                        required=True,
                        placeholder="热卖商品",
                    ),
                    ContentFieldCapability(
                        field_key="source_ref",
                        label="商品来源",
                        field_type="source_ref",
                        required=True,
                        placeholder="shelf.hot",
                    ),
                ],
            ),
        ],
    ),
    TemplateRegionCapability(
        template_region_code="content",
        label="内容营销区",
        description="品牌故事、活动说明或图文内容",
        required=False,
        default_region_name="内容营销",
        sort_order=40,
        block_slots=[
            BlockSlotCapability(
                slot_code="content.rich_text",
                label="图文内容",
                description="品牌故事或活动说明",
                block_type="rich_text",
                required=False,
                default_block_name="图文内容",
                sort_order=10,
                content_fields=[
                    ContentFieldCapability(
                        field_key="title",
                        label="标题",
                        field_type="text",
                        required=False,
                    ),
                    ContentFieldCapability(
                        field_key="body",
                        label="正文",
                        field_type="textarea",
                        required=True,
                    ),
                ],
            )
        ],
    ),
    TemplateRegionCapability(
        template_region_code="footer_promo",
        label="底部推荐区",
        description="底部推荐商品、补充说明或收尾营销",
        required=False,
        default_region_name="底部推荐",
        sort_order=50,
        block_slots=[
            BlockSlotCapability(
                slot_code="footer_promo.shelf",
                label="底部推荐货架",
                description="底部商品推荐",
                block_type="offer_shelf",
                required=False,
                default_block_name="底部推荐货架",
                sort_order=10,
                content_fields=[
                    ContentFieldCapability(
                        field_key="title",
                        label="货架标题",
                        field_type="text",
                        required=True,
                        placeholder="更多好物",
                    ),
                    ContentFieldCapability(
                        field_key="source_ref",
                        label="商品来源",
                        field_type="source_ref",
                        required=True,
                        placeholder="shelf.recommended",
                    ),
                ],
            )
        ],
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


def get_renderer_key(surface_code: str, block_type: str) -> str:
    for item in BLOCK_CAPABILITIES:
        if item.block_type == block_type:
            renderer_key = item.renderer_by_surface.get(surface_code)

            if renderer_key:
                return renderer_key

    raise HTTPException(status_code=422, detail="unsupported_block_renderer")


def _field_to_dto(field: ContentFieldCapability) -> ContentFieldDto:
    return ContentFieldDto(
        field_key=field.field_key,
        label=field.label,
        field_type=field.field_type,
        required=field.required,
        placeholder=field.placeholder,
        help_text=field.help_text,
    )


def _slot_to_dto(surface_code: str, slot: BlockSlotCapability) -> TemplateBlockSlotDto:
    return TemplateBlockSlotDto(
        slot_code=slot.slot_code,
        label=slot.label,
        description=slot.description,
        block_type=slot.block_type,
        renderer_key=get_renderer_key(surface_code, slot.block_type),
        required=slot.required,
        default_block_name=slot.default_block_name,
        sort_order=slot.sort_order,
        content_fields=[_field_to_dto(field) for field in slot.content_fields],
    )


def list_template_region_options(
    template_key: str,
    surface_code: str = "pc_web",
) -> list[TemplateRegionOption]:
    return [
        TemplateRegionOption(
            template_region_code=item.template_region_code,
            label=item.label,
            description=item.description,
            required=item.required,
            default_region_name=item.default_region_name,
            sort_order=item.sort_order,
            allowed_block_types=item.allowed_block_types,
            block_slots=[_slot_to_dto(surface_code, slot) for slot in item.block_slots],
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


def require_block_slot(
    template_key: str,
    slot_code: str,
) -> tuple[TemplateRegionCapability, BlockSlotCapability]:
    for region in list_template_region_capabilities(template_key):
        for slot in region.block_slots:
            if slot.slot_code == slot_code:
                return region, slot

    raise HTTPException(status_code=422, detail="unsupported_block_slot")


def require_block_type_allowed(
    surface_code: str,
    template_key: str,
    template_region_code: str,
    block_type: str,
) -> str:
    template_region = require_template_region(template_key, template_region_code)

    if block_type not in template_region.allowed_block_types:
        raise HTTPException(status_code=422, detail="block_type_not_allowed_for_region")

    return get_renderer_key(surface_code, block_type)
