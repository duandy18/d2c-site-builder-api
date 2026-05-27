from app.domains.site_builder.services.page_authoring_capabilities import (
    PC_HOME_STANDARD_TEMPLATE_KEY,
    list_block_options,
    list_region_block_rules,
    list_template_region_options,
)


def test_page_authoring_capabilities_contains_template_regions() -> None:
    template_regions = {
        item.template_region_code: item
        for item in list_template_region_options(PC_HOME_STANDARD_TEMPLATE_KEY)
    }
    block_types = {item.value for item in list_block_options()}
    rules = {
        item.template_region_code: set(item.allowed_block_types)
        for item in list_region_block_rules(PC_HOME_STANDARD_TEMPLATE_KEY)
    }

    assert set(template_regions) >= {
        "hero",
        "entry",
        "product_showcase",
        "content",
        "footer_promo",
    }
    assert "hero_banner" in block_types
    assert "entry_grid" in block_types
    assert "offer_shelf" in block_types
    assert "hero_banner" in rules["hero"]
    assert "entry_grid" in rules["entry"]
    assert "offer_shelf" in rules["product_showcase"]
