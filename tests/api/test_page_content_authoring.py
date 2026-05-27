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

    banner_slot = next(slot for slot in hero_group["slots"] if slot["slot_code"] == "hero.banner")
    field_by_key = {field["field_key"]: field for field in banner_slot["content_fields"]}

    assert field_by_key["image"]["value_type"] == "image"
    assert field_by_key["image"]["editor_type"] == "image_editor"
    assert field_by_key["link_target"]["value_type"] == "link_target"
    assert field_by_key["link_target"]["editor_type"] == "link_target_picker"


def test_entry_list_field_contract_is_structured() -> None:
    response = client.get(f"{BASE}/content-form")
    payload = response.json()

    entry_group = next(
        group for group in payload["groups"] if group["template_region_code"] == "entry"
    )
    entry_slot = next(slot for slot in entry_group["slots"] if slot["slot_code"] == "entry.grid")
    entries_field = next(
        field for field in entry_slot["content_fields"] if field["field_key"] == "entries"
    )

    assert entries_field["value_type"] == "entry_list"
    assert entries_field["editor_type"] == "entry_list_editor"

    item_field_keys = {field["field_key"] for field in entries_field["item_fields"]}
    assert {"title", "subtitle", "image", "link_target"} <= item_field_keys


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


def test_patch_banner_slot_content_uses_structured_image_and_link_target() -> None:
    response = client.patch(
        f"{BASE}/contents/hero.banner",
        json={
            "content": {
                "image": {
                    "type": "url",
                    "url": "https://example.com/banner.jpg",
                    "alt": "五月宠物用品大促",
                },
                "link_target": {
                    "type": "custom_path",
                    "path": "/campaign/may",
                },
                "title": "五月宠物用品大促",
            }
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["slot_code"] == "hero.banner"
    assert payload["block_code"] == "home.hero.banner"
    assert payload["content"]["image"]["url"] == "https://example.com/banner.jpg"
    assert payload["content"]["link_target"]["path"] == "/campaign/may"


def test_patch_slot_content_rejects_missing_required_field() -> None:
    response = client.patch(
        f"{BASE}/contents/hero.banner",
        json={"content": {"title": "缺少图片"}},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "missing_required_content_field:image"
