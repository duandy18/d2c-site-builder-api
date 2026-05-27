from app.domains.site_builder.services.page_authoring_capabilities import (
    list_block_options,
    list_region_block_rules,
    list_region_options,
)


def test_page_authoring_capabilities_contains_core_types() -> None:
    region_types = {item.value for item in list_region_options()}
    block_types = {item.value for item in list_block_options()}
    rules = {item.region_type: set(item.allowed_block_types) for item in list_region_block_rules()}

    assert "hero" in region_types
    assert "main" in region_types
    assert "hero_banner" in block_types
    assert "offer_shelf" in block_types
    assert "hero_banner" in rules["hero"]
    assert "offer_shelf" in rules["main"]
