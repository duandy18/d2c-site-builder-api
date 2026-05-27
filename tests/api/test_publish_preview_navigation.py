from fastapi.testclient import TestClient

from app.main import app


def test_publish_preview_page_is_registered_under_publish_center() -> None:
    client = TestClient(app)

    response = client.get("/admin/site-builder/navigation")

    assert response.status_code == 200

    payload = response.json()
    root_by_code = {page["page_code"]: page for page in payload["pages"]}

    publish = root_by_code["site_builder.publish"]
    child_by_code = {page["page_code"]: page for page in publish["children"]}

    assert "site_builder.publish.preview" in child_by_code
    assert "site_builder.publish.check" in child_by_code
    assert "site_builder.publish.runtime" in child_by_code

    preview = child_by_code["site_builder.publish.preview"]
    assert preview["title"] == "页面预览"
    assert preview["route_path"] == "/publish/preview"
    assert preview["component_key"] == "site_builder.publish.preview"
    assert preview["status"] == "connected"
    assert preview["is_active"] is True

    assert (
        child_by_code["site_builder.publish.preview"]["sort_order"]
        < child_by_code["site_builder.publish.check"]["sort_order"]
    )
