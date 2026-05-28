from app.core.db import get_session
from app.domains.site_builder.services.page_authoring_capabilities import (
    PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY,
    require_block_slot,
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


def test_template_slots_are_registered() -> None:
    session = next(_session())

    _, slot = require_block_slot(
        session,
        PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY,
        "campaign.banner",
    )

    fields = slot.content_schema_json.get("fields", {})

    assert slot.block_type == "campaign_banner"
    assert "title" in fields
    assert "subtitle" in fields


def test_product_grid_has_structured_source_and_products_fields() -> None:
    session = next(_session())

    _, slot = require_block_slot(
        session,
        PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY,
        "product_grid.list",
    )

    fields = slot.content_schema_json.get("fields", {})

    assert slot.block_type == "product_grid"
    assert "source" in fields
    assert "products" in fields
