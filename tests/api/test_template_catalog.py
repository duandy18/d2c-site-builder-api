from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_template_catalog_returns_terminal_pc_web_templates() -> None:
    response = client.get("/admin/site-builder/templates")

    assert response.status_code == 200

    payload = response.json()
    templates = {item["template_key"]: item for item in payload["templates"]}

    assert set(templates) == {
        "pc_home_simple_shop_v1",
        "pc_product_detail_gallery_v1",
        "pc_product_detail_image_matrix_v1",
    }

    home = templates["pc_home_simple_shop_v1"]
    assert home["surface_code"] == "pc_web"
    assert home["page_code"] == "home"
    assert home["route_path"] == "/pc-web/home"
    assert home["region_count"] == 8
    assert home["slot_count"] == 10
    assert home["field_count"] >= 1

    detail = templates["pc_product_detail_image_matrix_v1"]
    assert detail["route_path"] == "/pc-web/product-detail-image-matrix"
    assert any(
        region["template_region_code"] == "product.image_matrix" for region in detail["regions"]
    )


def test_template_catalog_exposes_schema_contracts() -> None:
    response = client.get("/admin/site-builder/templates")

    assert response.status_code == 200

    templates = response.json()["templates"]
    home = next(item for item in templates if item["template_key"] == "pc_home_simple_shop_v1")
    product_grid_region = next(
        region
        for region in home["regions"]
        if region["template_region_code"] == "home.product_grid"
    )
    product_grid_slot = next(
        slot for slot in product_grid_region["slots"] if slot["slot_code"] == "product_grid.list"
    )

    assert product_grid_slot["renderer_key"] == "pc_web.product_grid"
    assert "content_fields" not in product_grid_slot
    assert "content_schema" in product_grid_slot
    assert "products" in product_grid_slot["content_schema"]["fields"]
