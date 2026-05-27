from __future__ import annotations

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
PC_CATEGORY_ENTRY_TEMPLATE_KEY = "pc_category_entry_v1"
PC_PRODUCT_LIST_TEMPLATE_KEY = "pc_product_list_v1"
PC_CAMPAIGN_TEMPLATE_KEY = "pc_campaign_v1"
PC_CONTENT_PAGE_TEMPLATE_KEY = "pc_content_page_v1"


@dataclass(frozen=True)
class ContentFieldCapability:
    field_key: str
    label: str
    value_type: str
    editor_type: str
    required: bool
    placeholder: str | None = None
    help_text: str | None = None
    options: tuple[OptionItem, ...] = ()
    item_fields: tuple[ContentFieldCapability, ...] = ()

    @property
    def field_type(self) -> str:
        # Backward-compatible field for current frontend.
        return self.value_type


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


LINK_TARGET_OPTIONS = (
    OptionItem(value="none", label="不跳转", description="点击后不跳转"),
    OptionItem(value="custom_path", label="内部路径", description="站内路径，例如 /campaign/may"),
    OptionItem(value="external_url", label="外部链接", description="完整外部 URL"),
    OptionItem(value="category", label="分类页", description="跳转到分类或分组页"),
    OptionItem(value="offer", label="商品页", description="跳转到商品详情页"),
    OptionItem(value="campaign", label="活动页", description="跳转到活动页"),
    OptionItem(value="content_page", label="内容页", description="跳转到品牌故事或说明页"),
    OptionItem(value="search", label="搜索页", description="跳转到搜索结果页"),
)

OFFER_SOURCE_OPTIONS = (
    OptionItem(value="offer_group", label="商品组", description="预定义商品组，例如热卖商品"),
    OptionItem(value="manual_offer_list", label="手动商品列表", description="手动指定商品 ID 列表"),
    OptionItem(value="campaign_offer_group", label="活动商品组", description="活动页关联商品组"),
    OptionItem(value="category", label="分类来源", description="根据分类展示商品列表"),
    OptionItem(value="search_query", label="搜索条件", description="根据搜索条件展示商品列表"),
)

IMAGE_ITEM_FIELDS = (
    ContentFieldCapability(
        field_key="type",
        label="图片类型",
        value_type="select",
        editor_type="select",
        required=True,
        options=(OptionItem(value="url", label="图片 URL", description="通过 URL 引用图片"),),
    ),
    ContentFieldCapability(
        field_key="url",
        label="图片地址",
        value_type="url",
        editor_type="image_url_input",
        required=True,
        placeholder="https://example.com/banner.jpg",
    ),
    ContentFieldCapability(
        field_key="alt",
        label="图片说明",
        value_type="text",
        editor_type="text_input",
        required=False,
        placeholder="五月宠物用品大促",
    ),
)

LINK_TARGET_ITEM_FIELDS = (
    ContentFieldCapability(
        field_key="type",
        label="跳转类型",
        value_type="select",
        editor_type="select",
        required=True,
        options=LINK_TARGET_OPTIONS,
    ),
    ContentFieldCapability(
        field_key="path",
        label="内部路径",
        value_type="text",
        editor_type="text_input",
        required=False,
        placeholder="/campaign/may",
    ),
    ContentFieldCapability(
        field_key="url",
        label="外部链接",
        value_type="url",
        editor_type="url_input",
        required=False,
        placeholder="https://example.com",
    ),
    ContentFieldCapability(
        field_key="ref",
        label="引用编码",
        value_type="text",
        editor_type="text_input",
        required=False,
        placeholder="cat-litter / offer_001 / campaign_may",
    ),
)

ENTRY_LIST_ITEM_FIELDS = (
    ContentFieldCapability(
        field_key="title",
        label="入口标题",
        value_type="text",
        editor_type="text_input",
        required=True,
        placeholder="猫砂",
    ),
    ContentFieldCapability(
        field_key="subtitle",
        label="入口说明",
        value_type="text",
        editor_type="text_input",
        required=False,
        placeholder="除臭结团猫砂",
    ),
    ContentFieldCapability(
        field_key="image",
        label="入口图片",
        value_type="image",
        editor_type="image_editor",
        required=False,
        item_fields=IMAGE_ITEM_FIELDS,
    ),
    ContentFieldCapability(
        field_key="link_target",
        label="跳转目标",
        value_type="link_target",
        editor_type="link_target_picker",
        required=False,
        item_fields=LINK_TARGET_ITEM_FIELDS,
    ),
)

OFFER_SOURCE_ITEM_FIELDS = (
    ContentFieldCapability(
        field_key="type",
        label="来源类型",
        value_type="select",
        editor_type="select",
        required=True,
        options=OFFER_SOURCE_OPTIONS,
    ),
    ContentFieldCapability(
        field_key="ref",
        label="来源编码",
        value_type="text",
        editor_type="text_input",
        required=False,
        placeholder="hot / cat-litter / campaign_may",
    ),
    ContentFieldCapability(
        field_key="refs",
        label="手动商品列表",
        value_type="json",
        editor_type="json_debug",
        required=False,
        placeholder='["offer_001","offer_002"]',
    ),
)

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


def text_field(
    field_key: str,
    label: str,
    required: bool,
    placeholder: str | None = None,
) -> ContentFieldCapability:
    return ContentFieldCapability(
        field_key=field_key,
        label=label,
        value_type="text",
        editor_type="text_input",
        required=required,
        placeholder=placeholder,
    )


def textarea_field(
    field_key: str,
    label: str,
    required: bool,
    placeholder: str | None = None,
) -> ContentFieldCapability:
    return ContentFieldCapability(
        field_key=field_key,
        label=label,
        value_type="textarea",
        editor_type="textarea",
        required=required,
        placeholder=placeholder,
    )


def image_field(field_key: str, label: str, required: bool) -> ContentFieldCapability:
    return ContentFieldCapability(
        field_key=field_key,
        label=label,
        value_type="image",
        editor_type="image_editor",
        required=required,
        item_fields=IMAGE_ITEM_FIELDS,
    )


def link_target_field(
    field_key: str = "link_target",
    required: bool = False,
) -> ContentFieldCapability:
    return ContentFieldCapability(
        field_key=field_key,
        label="跳转目标",
        value_type="link_target",
        editor_type="link_target_picker",
        required=required,
        item_fields=LINK_TARGET_ITEM_FIELDS,
    )


def offer_source_field(field_key: str = "source", required: bool = True) -> ContentFieldCapability:
    return ContentFieldCapability(
        field_key=field_key,
        label="商品来源",
        value_type="offer_source",
        editor_type="offer_source_picker",
        required=required,
        item_fields=OFFER_SOURCE_ITEM_FIELDS,
    )


def entry_list_field(field_key: str = "entries", required: bool = True) -> ContentFieldCapability:
    return ContentFieldCapability(
        field_key=field_key,
        label="入口列表",
        value_type="entry_list",
        editor_type="entry_list_editor",
        required=required,
        item_fields=ENTRY_LIST_ITEM_FIELDS,
    )


def title_slot(
    slot_code: str,
    label: str,
    sort_order: int,
    required: bool = False,
) -> BlockSlotCapability:
    return BlockSlotCapability(
        slot_code=slot_code,
        label=label,
        description=f"{label}内容",
        block_type="title",
        required=required,
        default_block_name=label,
        sort_order=sort_order,
        content_fields=[
            text_field("title", "标题", True, label),
            text_field("subtitle", "副标题", False),
        ],
    )


def banner_slot(slot_code: str, label: str, sort_order: int, required: bool) -> BlockSlotCapability:
    return BlockSlotCapability(
        slot_code=slot_code,
        label=label,
        description=f"{label}图片和跳转目标",
        block_type="hero_banner",
        required=required,
        default_block_name=label,
        sort_order=sort_order,
        content_fields=[
            image_field("image", "图片", required),
            link_target_field(),
            text_field("title", "图片标题", False),
        ],
    )


def shelf_slot(slot_code: str, label: str, sort_order: int, required: bool) -> BlockSlotCapability:
    return BlockSlotCapability(
        slot_code=slot_code,
        label=label,
        description=f"{label}数据源",
        block_type="offer_shelf",
        required=required,
        default_block_name=label,
        sort_order=sort_order,
        content_fields=[
            text_field("title", "货架标题", True, label),
            offer_source_field(),
        ],
    )


def rich_text_slot(
    slot_code: str,
    label: str,
    sort_order: int,
    required: bool,
) -> BlockSlotCapability:
    return BlockSlotCapability(
        slot_code=slot_code,
        label=label,
        description=f"{label}正文内容",
        block_type="rich_text",
        required=required,
        default_block_name=label,
        sort_order=sort_order,
        content_fields=[
            text_field("title", "标题", False),
            textarea_field("body", "正文", True),
        ],
    )


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
                    text_field("title", "标题", True, "五月宠物用品大促"),
                    text_field("subtitle", "副标题", False, "猫砂猫粮限时优惠"),
                ],
            ),
            BlockSlotCapability(
                slot_code="hero.banner",
                label="首屏广告",
                description="首屏广告图和跳转目标",
                block_type="hero_banner",
                required=True,
                default_block_name="首屏广告",
                sort_order=20,
                content_fields=[
                    image_field("image", "广告图片", True),
                    link_target_field(),
                    text_field("title", "图片标题", False),
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
                    text_field("text", "促销文案", True, "满 99 减 20"),
                    link_target_field(),
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
                content_fields=[entry_list_field()],
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
            title_slot("product_showcase.title", "商品展示标题", 10),
            shelf_slot("product_showcase.shelf", "商品货架", 20, True),
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
            rich_text_slot("content.rich_text", "图文内容", 10, False),
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
            shelf_slot("footer_promo.shelf", "底部推荐货架", 10, False),
        ],
    ),
]

PC_CATEGORY_ENTRY_REGIONS = [
    TemplateRegionCapability(
        template_region_code="header",
        label="页面头部",
        description="分类入口页标题、说明和头图",
        required=True,
        default_region_name="分类入口页头部",
        sort_order=10,
        block_slots=[
            title_slot("header.title", "分类入口页标题", 10, True),
            banner_slot("header.banner", "分类入口页头图", 20, False),
        ],
    ),
    TemplateRegionCapability(
        template_region_code="entry",
        label="分类入口",
        description="分类、频道或活动入口列表",
        required=True,
        default_region_name="分类入口",
        sort_order=20,
        block_slots=[
            BlockSlotCapability(
                slot_code="entry.grid",
                label="分类入口宫格",
                description="分类入口页的入口列表",
                block_type="entry_grid",
                required=True,
                default_block_name="分类入口宫格",
                sort_order=10,
                content_fields=[entry_list_field()],
            )
        ],
    ),
    TemplateRegionCapability(
        template_region_code="recommended",
        label="推荐商品",
        description="分类入口页底部推荐商品",
        required=False,
        default_region_name="推荐商品",
        sort_order=30,
        block_slots=[
            shelf_slot("recommended.shelf", "推荐商品货架", 10, False),
        ],
    ),
]

PC_PRODUCT_LIST_REGIONS = [
    TemplateRegionCapability(
        template_region_code="header",
        label="列表头部",
        description="商品列表页标题、说明和头图",
        required=True,
        default_region_name="商品列表头部",
        sort_order=10,
        block_slots=[
            title_slot("header.title", "商品列表标题", 10, True),
            banner_slot("header.banner", "商品列表头图", 20, False),
        ],
    ),
    TemplateRegionCapability(
        template_region_code="listing",
        label="商品列表",
        description="商品列表页默认商品来源和空状态",
        required=True,
        default_region_name="商品列表",
        sort_order=20,
        block_slots=[
            BlockSlotCapability(
                slot_code="listing.source",
                label="商品列表来源",
                description="商品列表的数据来源",
                block_type="offer_shelf",
                required=True,
                default_block_name="商品列表来源",
                sort_order=10,
                content_fields=[
                    text_field("title", "列表标题", True, "全部商品"),
                    offer_source_field(),
                    text_field("empty_state_text", "空状态文案", False, "暂无可展示商品"),
                ],
            )
        ],
    ),
]

PC_CAMPAIGN_REGIONS = [
    TemplateRegionCapability(
        template_region_code="hero",
        label="活动首屏",
        description="活动页顶部主视觉和标题",
        required=True,
        default_region_name="活动首屏",
        sort_order=10,
        block_slots=[
            title_slot("hero.title", "活动标题", 10, True),
            banner_slot("hero.banner", "活动主图", 20, True),
            BlockSlotCapability(
                slot_code="hero.promotion",
                label="活动促销条",
                description="活动核心优惠文案",
                block_type="promotion_strip",
                required=False,
                default_block_name="活动促销条",
                sort_order=30,
                content_fields=[
                    text_field("text", "活动优惠文案", True, "限时优惠"),
                    link_target_field(),
                ],
            ),
        ],
    ),
    TemplateRegionCapability(
        template_region_code="products",
        label="活动商品",
        description="活动关联商品货架",
        required=True,
        default_region_name="活动商品",
        sort_order=20,
        block_slots=[
            shelf_slot("products.shelf", "活动商品货架", 10, True),
        ],
    ),
    TemplateRegionCapability(
        template_region_code="rules",
        label="活动说明",
        description="活动规则、时间和补充说明",
        required=False,
        default_region_name="活动说明",
        sort_order=30,
        block_slots=[
            rich_text_slot("rules.rich_text", "活动说明", 10, False),
        ],
    ),
]

PC_CONTENT_PAGE_REGIONS = [
    TemplateRegionCapability(
        template_region_code="article",
        label="内容正文",
        description="内容页标题、封面和正文",
        required=True,
        default_region_name="内容正文",
        sort_order=10,
        block_slots=[
            title_slot("article.title", "内容标题", 10, True),
            banner_slot("article.cover", "内容封面", 20, False),
            rich_text_slot("article.body", "正文内容", 30, True),
        ],
    ),
    TemplateRegionCapability(
        template_region_code="cta",
        label="行动引导",
        description="内容页底部行动引导",
        required=False,
        default_region_name="行动引导",
        sort_order=20,
        block_slots=[
            BlockSlotCapability(
                slot_code="cta.promotion",
                label="引导条",
                description="底部行动引导文案和跳转目标",
                block_type="promotion_strip",
                required=False,
                default_block_name="引导条",
                sort_order=10,
                content_fields=[
                    text_field("text", "引导文案", True, "查看相关商品"),
                    link_target_field(),
                ],
            )
        ],
    ),
]

TEMPLATE_NAMES = {
    PC_HOME_STANDARD_TEMPLATE_KEY: "标准电商首页",
    PC_CATEGORY_ENTRY_TEMPLATE_KEY: "分类入口页",
    PC_PRODUCT_LIST_TEMPLATE_KEY: "商品列表页",
    PC_CAMPAIGN_TEMPLATE_KEY: "活动页",
    PC_CONTENT_PAGE_TEMPLATE_KEY: "内容页",
}

TEMPLATE_REGIONS = {
    PC_HOME_STANDARD_TEMPLATE_KEY: PC_HOME_STANDARD_REGIONS,
    PC_CATEGORY_ENTRY_TEMPLATE_KEY: PC_CATEGORY_ENTRY_REGIONS,
    PC_PRODUCT_LIST_TEMPLATE_KEY: PC_PRODUCT_LIST_REGIONS,
    PC_CAMPAIGN_TEMPLATE_KEY: PC_CAMPAIGN_REGIONS,
    PC_CONTENT_PAGE_TEMPLATE_KEY: PC_CONTENT_PAGE_REGIONS,
}

TEMPLATE_BY_SURFACE_PAGE = {
    ("pc_web", "home"): PC_HOME_STANDARD_TEMPLATE_KEY,
    ("pc_web", "category_entry"): PC_CATEGORY_ENTRY_TEMPLATE_KEY,
    ("pc_web", "product_list"): PC_PRODUCT_LIST_TEMPLATE_KEY,
    ("pc_web", "campaign"): PC_CAMPAIGN_TEMPLATE_KEY,
    ("pc_web", "content_page"): PC_CONTENT_PAGE_TEMPLATE_KEY,
}


def get_template_key(surface_code: str, page_code: str) -> str:
    template_key = TEMPLATE_BY_SURFACE_PAGE.get((surface_code, page_code))

    if template_key:
        return template_key

    raise HTTPException(status_code=422, detail="unsupported_page_template")


def get_template_name(template_key: str) -> str:
    template_name = TEMPLATE_NAMES.get(template_key)

    if template_name:
        return template_name

    raise HTTPException(status_code=422, detail="unsupported_page_template")


def list_template_region_capabilities(
    template_key: str,
) -> list[TemplateRegionCapability]:
    template_regions = TEMPLATE_REGIONS.get(template_key)

    if template_regions is not None:
        return template_regions

    raise HTTPException(status_code=422, detail="unsupported_page_template")


def get_renderer_key(surface_code: str, block_type: str) -> str:
    for item in BLOCK_CAPABILITIES:
        if item.block_type == block_type:
            renderer_key = item.renderer_by_surface.get(surface_code)

            if renderer_key:
                return renderer_key

    raise HTTPException(status_code=422, detail="unsupported_block_renderer")


def content_field_to_dto(field: ContentFieldCapability) -> ContentFieldDto:
    return ContentFieldDto(
        field_key=field.field_key,
        label=field.label,
        field_type=field.field_type,
        value_type=field.value_type,
        editor_type=field.editor_type,
        required=field.required,
        placeholder=field.placeholder,
        help_text=field.help_text,
        options=list(field.options),
        item_fields=[content_field_to_dto(item) for item in field.item_fields],
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
        content_fields=[content_field_to_dto(field) for field in slot.content_fields],
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
