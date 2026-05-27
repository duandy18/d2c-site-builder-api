from typing import Any

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE = "/admin/site-builder/sites/default/surfaces/pc-web/pages/home"


def _ensure_region(
    template_region_code: str,
    region_name: str,
    sort_order: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "template_region_code": template_region_code,
        "region_name": region_name,
    }

    if sort_order is not None:
        payload["sort_order"] = sort_order

    response = client.post(f"{BASE}/regions", json=payload)

    if response.status_code == 200:
        return response.json()

    assert response.status_code == 409
    assert response.json()["detail"] == "template_region_already_enabled"

    draft_response = client.get(f"{BASE}/draft")
    assert draft_response.status_code == 200

    for region in draft_response.json()["regions"]:
        if region["template_region_code"] == template_region_code:
            return region

    raise AssertionError(f"enabled region not found: {template_region_code}")


def test_page_draft_returns_home_context() -> None:
    response = client.get(f"{BASE}/draft")

    assert response.status_code == 200
    payload = response.json()
    assert payload["site_code"] == "default"
    assert payload["surface_code"] == "pc_web"
    assert payload["page_code"] == "home"
    assert payload["template_key"] == "pc_home_standard_v1"
    assert isinstance(payload["regions"], list)


def test_page_planner_options_include_template_regions() -> None:
    response = client.get(f"{BASE}/planner-options")

    assert response.status_code == 200
    payload = response.json()

    assert payload["template_key"] == "pc_home_standard_v1"
    assert payload["template_name"] == "标准电商首页"

    template_regions = {
        item["template_region_code"]: item for item in payload["template_regions"]
    }
    assert set(template_regions) >= {
        "hero",
        "entry",
        "product_showcase",
        "content",
        "footer_promo",
    }
    assert template_regions["hero"]["required"] is True
    assert "entry_grid" in template_regions["entry"]["allowed_block_types"]
    assert "offer_shelf" in template_regions["product_showcase"]["allowed_block_types"]

    assert {item["value"] for item in payload["allowed_block_types"]} >= {
        "hero_banner",
        "entry_grid",
        "offer_shelf",
    }


def test_create_template_region_and_block() -> None:
    region = _ensure_region("hero", "首页首屏", 10)

    assert region["region_code"] == "home.hero"
    assert region["template_region_code"] == "hero"
    assert region["region_name"]
    assert "blocks" in region

    block_response = client.post(
        f"{BASE}/regions/{region['region_code']}/blocks",
        json={
            "block_name": "首页主广告",
            "block_type": "hero_banner",
            "sort_order": 10,
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
            },
            "layout": {},
        },
    )

    assert block_response.status_code == 200
    block = block_response.json()
    assert block["block_code"].startswith("home.hero.hero_banner")
    assert block["renderer_key"] == "pc_web.hero_banner"

    draft_response = client.get(f"{BASE}/draft")
    assert draft_response.status_code == 200

    draft = draft_response.json()
    assert any(item["region_code"] == "home.hero" for item in draft["regions"])


def test_create_duplicate_template_region_is_rejected() -> None:
    region = _ensure_region("entry", "快捷入口")
    assert region["template_region_code"] == "entry"

    second_response = client.post(
        f"{BASE}/regions",
        json={"template_region_code": "entry", "region_name": "重复入口"},
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "template_region_already_enabled"


def test_create_block_rejects_invalid_template_region_block_rule() -> None:
    region = _ensure_region("footer_promo", "底部推荐")

    block_response = client.post(
        f"{BASE}/regions/{region['region_code']}/blocks",
        json={
            "block_name": "主广告不应放底部推荐",
            "block_type": "hero_banner",
            "sort_order": 10,
            "content": {
                "image": {
                    "type": "url",
                    "url": "https://example.com/banner.jpg",
                }
            },
            "layout": {},
        },
    )

    assert block_response.status_code == 422
    assert block_response.json()["detail"] == "block_type_not_allowed_for_region"


def test_update_region_and_block() -> None:
    region = _ensure_region("product_showcase", "商品展示")

    update_region_response = client.patch(
        f"{BASE}/regions/{region['region_code']}",
        json={"region_name": "首页商品展示", "sort_order": 30},
    )

    assert update_region_response.status_code == 200
    assert update_region_response.json()["region_name"] == "首页商品展示"
    assert update_region_response.json()["sort_order"] == 30

    block_response = client.post(
        f"{BASE}/regions/{region['region_code']}/blocks",
        json={
            "block_name": "热卖商品",
            "block_type": "offer_shelf",
            "sort_order": 10,
            "content": {
                "title": "热卖商品",
                "source": {
                    "type": "offer_group",
                    "ref": "hot",
                },
            },
            "layout": {},
        },
    )
    assert block_response.status_code == 200

    block = block_response.json()

    update_block_response = client.patch(
        f"{BASE}/blocks/{block['block_code']}",
        json={
            "block_name": "热卖商品货架",
            "content": {
                "title": "热卖商品",
                "source": {
                    "type": "offer_group",
                    "ref": "hot-updated",
                },
            },
        },
    )

    assert update_block_response.status_code == 200
    updated = update_block_response.json()
    assert updated["block_name"] == "热卖商品货架"
    assert updated["content"]["source"]["ref"] == "hot-updated"
