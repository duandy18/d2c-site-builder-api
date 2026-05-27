from app.domains.site_builder.services.pc_home import get_planner_options


def test_get_planner_options_contains_core_types() -> None:
    options = get_planner_options()

    region_types = {item.value for item in options.allowed_region_types}
    block_types = {item.value for item in options.allowed_block_types}

    assert "hero" in region_types
    assert "main" in region_types
    assert "hero_banner" in block_types
    assert "offer_shelf" in block_types
