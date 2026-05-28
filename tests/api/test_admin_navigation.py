from fastapi.testclient import TestClient

from app.main import app


def test_site_builder_navigation_returns_registered_pages() -> None:
    client = TestClient(app)

    response = client.get("/admin/site-builder/navigation")

    assert response.status_code == 200

    payload = response.json()
    assert payload["app_code"] == "d2c-site-builder"

    root_by_code = {page["page_code"]: page for page in payload["pages"]}
    assert "site_builder.templates" in root_by_code
    assert "site_builder.pc_web" in root_by_code
    assert "site_builder.publish" in root_by_code
    assert "site_builder.settings" in root_by_code

    assert "site_builder.dashboard" not in root_by_code

    templates = root_by_code["site_builder.templates"]
    assert templates["title"] == "建站模板"
    assert templates["route_path"] == "/"
    assert templates["component_key"] == "layout.group"
    assert templates["status"] == "connected"

    template_child_by_code = {page["page_code"]: page for page in templates["children"]}

    assert set(template_child_by_code) == {
        "site_builder.templates.pc_web",
        "site_builder.templates.mobile_web",
        "site_builder.templates.mini_program",
    }

    pc_web_template = template_child_by_code["site_builder.templates.pc_web"]
    assert pc_web_template["title"] == "PC Web 模板"
    assert pc_web_template["route_path"] == "/templates/pc-web"
    assert pc_web_template["component_key"] == "site_builder.template_catalog"
    assert pc_web_template["status"] == "connected"

    mobile_web_template = template_child_by_code["site_builder.templates.mobile_web"]
    assert mobile_web_template["title"] == "手机 Web 模板"
    assert mobile_web_template["route_path"] == "/templates/mobile-web"
    assert mobile_web_template["component_key"] == "site_builder.template_catalog"
    assert mobile_web_template["status"] == "planned"

    mini_program_template = template_child_by_code["site_builder.templates.mini_program"]
    assert mini_program_template["title"] == "小程序模板"
    assert mini_program_template["route_path"] == "/templates/mini-program"
    assert mini_program_template["component_key"] == "site_builder.template_catalog"
    assert mini_program_template["status"] == "planned"

    pc_web = root_by_code["site_builder.pc_web"]
    child_by_code = {page["page_code"]: page for page in pc_web["children"]}

    assert set(child_by_code) == {
        "site_builder.pc_web.home",
        "site_builder.pc_web.product_detail_gallery",
        "site_builder.pc_web.product_detail_image_matrix",
    }

    home = child_by_code["site_builder.pc_web.home"]
    assert home["title"] == "首页搭建"
    assert home["route_path"] == "/pc-web/home"
    assert home["component_key"] == "site_builder.pc_web.home"
    assert home["status"] == "connected"

    gallery = child_by_code["site_builder.pc_web.product_detail_gallery"]
    assert gallery["title"] == "商品详情页A"
    assert gallery["route_path"] == "/pc-web/product-detail-gallery"
    assert gallery["component_key"] == "site_builder.pc_web.template_content"
    assert gallery["status"] == "connected"

    image_matrix = child_by_code["site_builder.pc_web.product_detail_image_matrix"]
    assert image_matrix["title"] == "商品详情页B"
    assert image_matrix["route_path"] == "/pc-web/product-detail-image-matrix"
    assert image_matrix["component_key"] == "site_builder.pc_web.template_content"
    assert image_matrix["status"] == "connected"
