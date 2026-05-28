import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_terminal_template_routes_are_registered_in_navigation() -> None:
    response = client.get("/admin/site-builder/navigation")

    assert response.status_code == 200

    payload_text = json.dumps(response.json(), ensure_ascii=False)

    assert "/pc-web/home" in payload_text
    assert "/pc-web/product-detail-gallery" in payload_text
    assert "/pc-web/product-detail-image-matrix" in payload_text

    assert "/pc-web/category-entry" not in payload_text
    assert "/pc-web/product-list" not in payload_text
    assert "/pc-web/campaign" not in payload_text
    assert "/pc-web/content-page" not in payload_text
