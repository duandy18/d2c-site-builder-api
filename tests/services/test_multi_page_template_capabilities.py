from app.core.db import get_session
from app.domains.site_builder.services.page_authoring_capabilities import (
    PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY,
    PC_PRODUCT_DETAIL_GALLERY_TEMPLATE_KEY,
    PC_PRODUCT_DETAIL_IMAGE_MATRIX_TEMPLATE_KEY,
    require_block_slot,
    require_template_name,
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


def test_template_names_are_defined_in_db() -> None:
    session = next(_session())

    assert require_template_name(session, PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY) == "极简商品型首页"
    assert (
        require_template_name(session, PC_PRODUCT_DETAIL_GALLERY_TEMPLATE_KEY)
        == "标准图册商品详情页"
    )
    assert (
        require_template_name(session, PC_PRODUCT_DETAIL_IMAGE_MATRIX_TEMPLATE_KEY)
        == "多图展示商品详情页"
    )


def test_simple_shop_slots_are_registered() -> None:
    session = next(_session())

    _, product_grid_slot = require_block_slot(
        session,
        PC_HOME_SIMPLE_SHOP_TEMPLATE_KEY,
        "product_grid.list",
    )
    _, gallery_slot = require_block_slot(
        session,
        PC_PRODUCT_DETAIL_GALLERY_TEMPLATE_KEY,
        "product.gallery.thumbs",
    )
    _, matrix_slot = require_block_slot(
        session,
        PC_PRODUCT_DETAIL_IMAGE_MATRIX_TEMPLATE_KEY,
        "product.image_matrix.side_images",
    )

    assert product_grid_slot.block_type == "product_grid"
    assert gallery_slot.block_type == "product_gallery_thumbs"
    assert matrix_slot.block_type == "product_image_matrix_side_images"
