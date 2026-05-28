from app.core.db import get_session
from app.domains.site_builder.services.page_authoring_capabilities import (
    PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY,
    list_block_options,
    list_region_block_rules,
    list_template_region_options,
)


def _session():
    dependency = get_session()
    session = next(dependency)
    try:
        yield session
    finally:
        try:
            next(dependency)
        except StopIteration:
            pass


def test_page_authoring_capabilities_contains_simple_shop_template_regions() -> None:
    session = next(_session())

    template_regions = {
        item.template_region_code: item
        for item in list_template_region_options(session, PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY)
    }
    block_types = {item.value for item in list_block_options(session)}
    rules = {
        item.template_region_code: set(item.allowed_block_types)
        for item in list_region_block_rules(session, PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY)
    }

    assert set(template_regions) >= {
        "home.header",
        "home.product_collection",
        "home.hero",
        "home.campaign",
        "home.product_category",
        "home.product_grid",
        "home.service",
        "home.legal_footer",
    }
    assert "product_grid" in block_types
    assert "campaign_banner" in block_types
    assert "product_grid" in rules["home.product_grid"]
    assert "cart_icon_link" in rules["home.product_category"]
