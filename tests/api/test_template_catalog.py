from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_template_catalog_returns_pc_web_templates() -> None:
    response = client.get("/admin/site-builder/templates")

    assert response.status_code == 200

    payload = response.json()
    templates = {item["template_key"]: item for item in payload["templates"]}

    assert set(templates) >= {
        "pc_home_standard_v1",
        "pc_category_entry_v1",
        "pc_product_list_v1",
        "pc_campaign_v1",
        "pc_content_page_v1",
    }

    home = templates["pc_home_standard_v1"]
    assert home["surface_code"] == "pc_web"
    assert home["page_code"] == "home"
    assert home["route_path"] == "/pc-web/home"
    assert home["region_count"] >= 1
    assert home["slot_count"] >= 1
    assert home["field_count"] >= 1

    campaign = templates["pc_campaign_v1"]
    assert campaign["route_path"] == "/pc-web/campaign"
    assert any(region["template_region_code"] == "hero" for region in campaign["regions"])


def test_template_catalog_exposes_slot_field_contracts() -> None:
    response = client.get("/admin/site-builder/templates")

    assert response.status_code == 200

    templates = response.json()["templates"]
    category = next(
        item for item in templates if item["template_key"] == "pc_category_entry_v1"
    )
    entry_region = next(
        region for region in category["regions"] if region["template_region_code"] == "entry"
    )
    entry_slot = next(slot for slot in entry_region["slots"] if slot["slot_code"] == "entry.grid")
    entries_field = next(
        field for field in entry_slot["content_fields"] if field["field_key"] == "entries"
    )

    assert entries_field["value_type"] == "entry_list"
    assert entries_field["editor_type"] == "entry_list_editor"
    assert {field["field_key"] for field in entries_field["item_fields"]} >= {
        "title",
        "image",
        "link_target",
    }
