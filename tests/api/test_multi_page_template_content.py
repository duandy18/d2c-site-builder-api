from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE = "/admin/site-builder/sites/default/surfaces/pc-web/pages"


def test_category_entry_content_form() -> None:
    response = client.get(f"{BASE}/category-entry/content-form")

    assert response.status_code == 200

    payload = response.json()
    assert payload["page_code"] == "category_entry"
    assert payload["template_key"] == "pc_category_entry_v1"

    group_codes = {group["template_region_code"] for group in payload["groups"]}
    assert {"header", "entry", "recommended"} <= group_codes

    entry_group = next(
        group for group in payload["groups"] if group["template_region_code"] == "entry"
    )
    entry_slot = next(
        slot for slot in entry_group["slots"] if slot["slot_code"] == "entry.grid"
    )
    entries_field = next(
        field for field in entry_slot["content_fields"] if field["field_key"] == "entries"
    )

    assert entries_field["value_type"] == "entry_list"
    assert entries_field["editor_type"] == "entry_list_editor"


def test_product_list_content_form() -> None:
    response = client.get(f"{BASE}/product-list/content-form")

    assert response.status_code == 200

    payload = response.json()
    assert payload["page_code"] == "product_list"
    assert payload["template_key"] == "pc_product_list_v1"

    listing_group = next(
        group for group in payload["groups"] if group["template_region_code"] == "listing"
    )
    source_slot = next(
        slot for slot in listing_group["slots"] if slot["slot_code"] == "listing.source"
    )
    source_field = next(
        field for field in source_slot["content_fields"] if field["field_key"] == "source"
    )

    assert source_field["value_type"] == "offer_source"
    assert source_field["editor_type"] == "offer_source_picker"


def test_campaign_content_form_and_patch() -> None:
    form_response = client.get(f"{BASE}/campaign/content-form")

    assert form_response.status_code == 200
    assert form_response.json()["template_key"] == "pc_campaign_v1"

    patch_response = client.patch(
        f"{BASE}/campaign/contents/hero.banner",
        json={
            "content": {
                "image": {
                    "type": "url",
                    "url": "https://example.com/campaign.jpg",
                    "alt": "五月活动",
                },
                "link_target": {
                    "type": "custom_path",
                    "path": "/campaign/may",
                },
                "title": "五月活动",
            }
        },
    )

    assert patch_response.status_code == 200
    payload = patch_response.json()
    assert payload["block_code"] == "campaign.hero.banner"
    assert payload["renderer_key"] == "pc_web.hero_banner"


def test_content_page_content_form_and_patch() -> None:
    form_response = client.get(f"{BASE}/content-page/content-form")

    assert form_response.status_code == 200
    assert form_response.json()["template_key"] == "pc_content_page_v1"

    patch_response = client.patch(
        f"{BASE}/content-page/contents/article.body",
        json={"content": {"title": "品牌故事", "body": "我们专注宠物用品。"}},
    )

    assert patch_response.status_code == 200
    payload = patch_response.json()
    assert payload["block_code"] == "content_page.article.body"
    assert payload["renderer_key"] == "pc_web.rich_text"

    draft_response = client.get(f"{BASE}/content-page/draft")
    assert draft_response.status_code == 200
    draft = draft_response.json()
    assert draft["template_key"] == "pc_content_page_v1"
    assert draft["regions"][0]["template_region_code"] == "article"
