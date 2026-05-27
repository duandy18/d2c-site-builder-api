from fastapi.testclient import TestClient

from app.main import app


def test_site_builder_navigation_returns_registered_pages() -> None:
    client = TestClient(app)

    response = client.get("/admin/site-builder/navigation")

    assert response.status_code == 200

    payload = response.json()
    assert payload["app_code"] == "d2c-site-builder"

    root_codes = {page["page_code"] for page in payload["pages"]}
    assert "site_builder.dashboard" in root_codes
    assert "site_builder.pc_web" in root_codes
    assert "site_builder.publish" in root_codes
    assert "site_builder.settings" in root_codes

    pc_web = next(page for page in payload["pages"] if page["page_code"] == "site_builder.pc_web")
    child_codes = {page["page_code"] for page in pc_web["children"]}

    assert "site_builder.pc_web.home" in child_codes
    assert "site_builder.pc_web.templates" in child_codes
    assert "site_builder.pc_web.category_entry" in child_codes
    assert "site_builder.pc_web.product_list" in child_codes
    assert "site_builder.pc_web.campaign" in child_codes
    assert "site_builder.pc_web.content_page" in child_codes

    assert "site_builder.pc_web.overview" not in child_codes
    assert "site_builder.pc_web.layout" not in child_codes
    assert "site_builder.pc_web.product_detail" not in child_codes

    home = next(
        page for page in pc_web["children"] if page["page_code"] == "site_builder.pc_web.home"
    )
    assert home["route_path"] == "/pc-web/home"
    assert home["component_key"] == "site_builder.pc_web.home"
    assert home["status"] == "connected"

    templates = next(
        page
        for page in pc_web["children"]
        if page["page_code"] == "site_builder.pc_web.templates"
    )
    assert templates["route_path"] == "/pc-web/templates"
    assert templates["component_key"] == "site_builder.pc_web.template_catalog"
    assert templates["status"] == "connected"
