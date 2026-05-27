from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ADMIN_BASE = "/admin/site-builder/sites/default/surfaces/pc-web/pages"
RUNTIME_BASE = "/runtime/site-builder/sites/default/surfaces/pc-web/pages"


def test_runtime_page_contract_returns_template_slots_without_editor_fields() -> None:
    response = client.get(f"{RUNTIME_BASE}/home")

    assert response.status_code == 200

    payload = response.json()
    assert payload["contract_type"] == "site_builder.page"
    assert payload["contract_version"] == "draft-preview-v1"
    assert payload["status"] == "draft_preview"
    assert payload["site_code"] == "default"
    assert payload["surface_code"] == "pc_web"
    assert payload["page_code"] == "home"
    assert payload["template_key"] == "pc_home_standard_v1"

    hero = next(
        region
        for region in payload["regions"]
        if region["template_region_code"] == "hero"
    )
    assert hero["region_code"] == "home.hero"
    assert hero["status"] in {"active", "empty"}

    banner = next(block for block in hero["blocks"] if block["slot_code"] == "hero.banner")
    assert banner["block_code"] == "home.hero.banner"
    assert banner["block_type"] == "hero_banner"
    assert banner["renderer_key"] == "pc_web.hero_banner"
    assert banner["required"] is True
    assert "content_fields" not in banner
    assert "editor_type" not in banner


def test_runtime_page_contract_includes_active_slot_content() -> None:
    patch_response = client.patch(
        f"{ADMIN_BASE}/campaign/contents/hero.banner",
        json={
            "content": {
                "image": {
                    "type": "url",
                    "url": "https://placehold.co/1600x520?text=Runtime+Campaign",
                    "alt": "Runtime Campaign",
                },
                "link_target": {
                    "type": "custom_path",
                    "path": "/pc-web/product-list",
                },
                "title": "Runtime Campaign",
            }
        },
    )

    assert patch_response.status_code == 200

    response = client.get(f"{RUNTIME_BASE}/campaign")

    assert response.status_code == 200

    payload = response.json()
    assert payload["template_key"] == "pc_campaign_v1"

    hero = next(
        region
        for region in payload["regions"]
        if region["template_region_code"] == "hero"
    )
    assert hero["status"] == "active"

    banner = next(block for block in hero["blocks"] if block["slot_code"] == "hero.banner")
    assert banner["status"] == "active"
    assert banner["is_filled"] is True
    assert banner["content"]["title"] == "Runtime Campaign"
    assert banner["content"]["image"]["url"] == (
        "https://placehold.co/1600x520?text=Runtime+Campaign"
    )


def test_runtime_page_contract_404_for_unknown_page() -> None:
    response = client.get(f"{RUNTIME_BASE}/missing-page")

    assert response.status_code == 404
    assert response.json()["detail"] == "page_not_found"
