from app.domains.site_builder.services.page_authoring_capabilities import (
    PC_CAMPAIGN_TEMPLATE_KEY,
    PC_CATEGORY_ENTRY_TEMPLATE_KEY,
    PC_CONTENT_PAGE_TEMPLATE_KEY,
    PC_PRODUCT_LIST_TEMPLATE_KEY,
    get_template_key,
    get_template_name,
    require_block_slot,
)


def test_page_codes_resolve_to_template_keys() -> None:
    assert get_template_key("pc_web", "category_entry") == PC_CATEGORY_ENTRY_TEMPLATE_KEY
    assert get_template_key("pc_web", "product_list") == PC_PRODUCT_LIST_TEMPLATE_KEY
    assert get_template_key("pc_web", "campaign") == PC_CAMPAIGN_TEMPLATE_KEY
    assert get_template_key("pc_web", "content_page") == PC_CONTENT_PAGE_TEMPLATE_KEY


def test_template_names_are_defined() -> None:
    assert get_template_name(PC_CATEGORY_ENTRY_TEMPLATE_KEY) == "分类入口页"
    assert get_template_name(PC_PRODUCT_LIST_TEMPLATE_KEY) == "商品列表页"
    assert get_template_name(PC_CAMPAIGN_TEMPLATE_KEY) == "活动页"
    assert get_template_name(PC_CONTENT_PAGE_TEMPLATE_KEY) == "内容页"


def test_multi_page_slots_are_registered() -> None:
    _, category_slot = require_block_slot(PC_CATEGORY_ENTRY_TEMPLATE_KEY, "entry.grid")
    _, product_slot = require_block_slot(PC_PRODUCT_LIST_TEMPLATE_KEY, "listing.source")
    _, campaign_slot = require_block_slot(PC_CAMPAIGN_TEMPLATE_KEY, "products.shelf")
    _, content_slot = require_block_slot(PC_CONTENT_PAGE_TEMPLATE_KEY, "article.body")

    assert category_slot.block_type == "entry_grid"
    assert product_slot.block_type == "offer_shelf"
    assert campaign_slot.block_type == "offer_shelf"
    assert content_slot.block_type == "rich_text"
