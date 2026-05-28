from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
BASE = "/admin/site-builder/sites/default/surfaces/pc-web/pages"


def test_product_detail_gallery_content_form() -> None:
    response = client.get(f"{BASE}/product-detail-gallery/content-form")

    assert response.status_code == 200

    payload = response.json()
    assert payload["page_code"] == "product_detail_gallery"
    assert payload["template_key"] == "pc_product_detail_gallery_v1"

    group_codes = {group["template_region_code"] for group in payload["groups"]}
    assert {"product.gallery", "product.summary", "product.detail_content"} <= group_codes


def test_product_detail_image_matrix_content_form() -> None:
    response = client.get(f"{BASE}/product-detail-image-matrix/content-form")

    assert response.status_code == 200

    payload = response.json()
    assert payload["page_code"] == "product_detail_image_matrix"
    assert payload["template_key"] == "pc_product_detail_image_matrix_v1"

    matrix_group = next(
        group
        for group in payload["groups"]
        if group["template_region_code"] == "product.image_matrix"
    )
    slot = next(
        item
        for item in matrix_group["slots"]
        if item["slot_code"] == "product.image_matrix.side_images"
    )

    assert slot["renderer_key"] == "pc_web.product_image_matrix_side_images"
    assert "images" in slot["content_schema"]["fields"]
