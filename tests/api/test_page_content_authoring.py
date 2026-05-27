from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE = "/admin/site-builder/sites/default/surfaces/pc-web/pages/home"


def test_content_form_returns_template_slots() -> None:
    response = client.get(f"{BASE}/content-form")

    assert response.status_code == 200

    payload = response.json()
    assert payload["template_key"] == "pc_home_standard_v1"

    hero_group = next(
        group for group in payload["groups"] if group["template_region_code"] == "hero"
    )
    slot_codes = {slot["slot_code"] for slot in hero_group["slots"]}

    assert "hero.title" in slot_codes
    assert "hero.banner" in slot_codes
    assert "hero.promotion" in slot_codes


def test_patch_slot_content_creates_region_and_block() -> None:
    response = client.patch(
        f"{BASE}/contents/content.rich_text",
        json={"content": {"title": "品牌故事", "body": "我们专注宠物用品。"}},
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["slot_code"] == "content.rich_text"
    assert payload["block_code"] == "home.content.rich_text"
    assert payload["renderer_key"] == "pc_web.rich_text"
    assert payload["content"]["body"] == "我们专注宠物用品。"

    draft_response = client.get(f"{BASE}/draft")
    draft = draft_response.json()

    content_region = next(
        region for region in draft["regions"] if region["template_region_code"] == "content"
    )
    assert content_region["region_code"] == "home.content"
    assert content_region["blocks"][0]["block_code"] == "home.content.rich_text"


def test_patch_slot_content_rejects_missing_required_field() -> None:
    response = client.patch(
        f"{BASE}/contents/hero.banner",
        json={"content": {"title": "缺少图片"}},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "missing_required_content_field:image_url"
