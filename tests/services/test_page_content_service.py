from app.domains.site_builder.services.page_authoring_capabilities import (
    PC_HOME_STANDARD_TEMPLATE_KEY,
    require_block_slot,
)


def test_template_slots_are_registered() -> None:
    _, slot = require_block_slot(PC_HOME_STANDARD_TEMPLATE_KEY, "hero.banner")

    field_keys = {field.field_key for field in slot.content_fields}

    assert slot.block_type == "hero_banner"
    assert "image" in field_keys
    assert "link_target" in field_keys


def test_entry_grid_has_entry_list_field() -> None:
    _, slot = require_block_slot(PC_HOME_STANDARD_TEMPLATE_KEY, "entry.grid")

    entries_field = next(field for field in slot.content_fields if field.field_key == "entries")
    item_field_keys = {field.field_key for field in entries_field.item_fields}

    assert entries_field.value_type == "entry_list"
    assert entries_field.editor_type == "entry_list_editor"
    assert {"title", "subtitle", "image", "link_target"} <= item_field_keys
