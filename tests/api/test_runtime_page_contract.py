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
    assert payload["template_key"] == "pc_home_simple_shop_v1"

    campaign = next(
        region for region in payload["regions"] if region["template_region_code"] == "home.campaign"
    )
    assert campaign["region_code"] == "home.home.campaign"
    assert campaign["status"] in {"active", "empty"}

    banner = next(block for block in campaign["blocks"] if block["slot_code"] == "campaign.banner")
    assert banner["block_code"] == "home.campaign.banner"
    assert banner["block_type"] == "campaign_banner"
    assert banner["renderer_key"] == "pc_web.campaign_banner"
    assert banner["required"] is True
    assert "content_fields" not in banner
    assert "editor_type" not in banner
    assert "layout" not in banner
    assert "presentation" in banner


def test_runtime_page_contract_includes_active_slot_content_and_presentation() -> None:
    patch_response = client.patch(
        f"{ADMIN_BASE}/home/contents/campaign.banner",
        json={
            "content": {
                "label": "大促活动",
                "title": "满 99 减 20",
                "subtitle": "猫砂猫粮组合优惠",
                "link_target": {"type": "custom_path", "path": "/campaign/may"},
            },
            "presentation": {"tone": "dark"},
        },
    )

    assert patch_response.status_code == 200

    response = client.get(f"{RUNTIME_BASE}/home")

    assert response.status_code == 200

    payload = response.json()
    assert payload["template_key"] == "pc_home_simple_shop_v1"

    campaign = next(
        region for region in payload["regions"] if region["template_region_code"] == "home.campaign"
    )
    assert campaign["status"] == "active"

    banner = next(block for block in campaign["blocks"] if block["slot_code"] == "campaign.banner")
    assert banner["status"] == "active"
    assert banner["is_filled"] is True
    assert banner["content"]["title"] == "满 99 减 20"
    assert banner["presentation"]["tone"] == "dark"


def test_runtime_page_contract_returns_product_detail_templates() -> None:
    gallery_response = client.get(f"{RUNTIME_BASE}/product-detail-gallery")
    matrix_response = client.get(f"{RUNTIME_BASE}/product-detail-image-matrix")

    assert gallery_response.status_code == 200
    assert matrix_response.status_code == 200
    assert gallery_response.json()["template_key"] == "pc_product_detail_gallery_v1"
    assert matrix_response.json()["template_key"] == "pc_product_detail_image_matrix_v1"


def test_runtime_page_contract_404_for_unknown_page() -> None:
    response = client.get(f"{RUNTIME_BASE}/missing-page")

    assert response.status_code == 404
    assert response.json()["detail"] == "page_not_found"
