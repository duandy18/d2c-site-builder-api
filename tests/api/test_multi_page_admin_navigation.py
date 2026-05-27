import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_multi_page_template_routes_are_registered_in_navigation() -> None:
    response = client.get("/admin/site-builder/navigation")

    assert response.status_code == 200

    payload_text = json.dumps(response.json(), ensure_ascii=False)

    assert "/pc-web/category-entry" in payload_text
    assert "/pc-web/product-list" in payload_text
    assert "/pc-web/campaign" in payload_text
    assert "/pc-web/content-page" in payload_text

    assert "/pc-web/category-landing" not in payload_text
    assert "/pc-web/campaigns" not in payload_text
    assert "/pc-web/content-pages" not in payload_text

    assert "site_builder.pc_web.template_content" in payload_text
