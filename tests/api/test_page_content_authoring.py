from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE = "/admin/site-builder/sites/default/surfaces/pc-web/pages/home"


def test_content_form_returns_template_slots() -> None:
    response = client.get(f"{BASE}/content-form")

    assert response.status_code == 200

    payload = response.json()
    assert payload["template_key"] == "pc_home_simple_shop_v1"

    campaign_group = next(
        group for group in payload["groups"] if group["template_region_code"] == "home.campaign"
    )
    slot_codes = {slot["slot_code"] for slot in campaign_group["slots"]}

    assert "campaign.banner" in slot_codes

    banner_slot = next(
        slot for slot in campaign_group["slots"] if slot["slot_code"] == "campaign.banner"
    )
    assert banner_slot["renderer_key"] == "pc_web.campaign_banner"
    assert "content_schema" in banner_slot
    assert "presentation_schema" in banner_slot


def test_patch_slot_content_creates_region_and_block() -> None:
    response = client.patch(
        f"{BASE}/contents/campaign.banner",
        json={
            "content": {
                "label": "大促活动",
                "title": "满 99 减 20",
                "subtitle": "猫砂猫粮组合优惠",
            },
            "presentation": {"tone": "dark"},
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["slot_code"] == "campaign.banner"
    assert payload["block_code"] == "home.campaign.banner"
    assert payload["renderer_key"] == "pc_web.campaign_banner"
    assert payload["content"]["title"] == "满 99 减 20"
    assert payload["presentation"]["tone"] == "dark"

    draft_response = client.get(f"{BASE}/draft")
    draft = draft_response.json()

    campaign_region = next(
        region for region in draft["regions"] if region["template_region_code"] == "home.campaign"
    )
    assert campaign_region["region_code"] == "home.home.campaign"
    assert campaign_region["blocks"][0]["block_code"] == "home.campaign.banner"


def test_patch_slot_content_rejects_missing_required_field() -> None:
    response = client.patch(
        f"{BASE}/contents/campaign.banner",
        json={"content": {"title": ""}},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "missing_required_content_field:title"
