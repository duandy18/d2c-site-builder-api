from app.domains.site_builder.services.page_authoring_capabilities import (
    PC_HOME_STANDARD_TEMPLATE_KEY,
    require_block_slot,
)


def test_template_slots_are_registered() -> None:
    _, slot = require_block_slot(PC_HOME_STANDARD_TEMPLATE_KEY, "hero.banner")

    field_keys = {field.field_key for field in slot.content_fields}

    assert slot.block_type == "hero_banner"
    assert "image_url" in field_keys
    assert "link_url" in field_keys
