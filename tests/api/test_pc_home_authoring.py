from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE = "/admin/site-builder/sites/default/surfaces/pc-web/pages/home"


def test_page_draft_returns_home_context() -> None:
    response = client.get(f"{BASE}/draft")

    assert response.status_code == 200
    assert response.json()["site_code"] == "default"
    assert response.json()["surface_code"] == "pc_web"
    assert response.json()["page_code"] == "home"
    assert isinstance(response.json()["regions"], list)


def test_page_planner_options_include_region_block_rules() -> None:
    response = client.get(f"{BASE}/planner-options")

    assert response.status_code == 200
    payload = response.json()

    assert {item["value"] for item in payload["allowed_region_types"]} >= {"hero", "main"}
    assert {item["value"] for item in payload["allowed_block_types"]} >= {
        "hero_banner",
        "offer_shelf",
    }

    rules = {
        item["region_type"]: set(item["allowed_block_types"])
        for item in payload["region_block_rules"]
    }
    assert "hero_banner" in rules["hero"]
    assert "offer_shelf" in rules["main"]


def test_create_region_and_block() -> None:
    region_response = client.post(
        f"{BASE}/regions",
        json={"region_name": "头图区域", "region_type": "hero", "sort_order": 10},
    )

    assert region_response.status_code == 200
    region = region_response.json()
    assert region["region_code"].startswith("home.hero")
    assert region["region_name"] == "头图区域"
    assert region["blocks"] == []

    block_response = client.post(
        f"{BASE}/regions/{region['region_code']}/blocks",
        json={
            "block_name": "首页主广告",
            "block_type": "hero_banner",
            "sort_order": 10,
            "content": {"title": "五月宠物用品大促"},
            "layout": {"height": 320},
        },
    )

    assert block_response.status_code == 200
    block = block_response.json()
    assert block["block_code"].startswith(f"{region['region_code']}.hero_banner")
    assert block["renderer_key"] == "pc_web.hero_banner"

    draft_response = client.get(f"{BASE}/draft")
    assert draft_response.status_code == 200

    draft = draft_response.json()
    assert any(item["region_code"] == region["region_code"] for item in draft["regions"])


def test_create_block_rejects_invalid_region_block_rule() -> None:
    region_response = client.post(
        f"{BASE}/regions",
        json={"region_name": "推荐区域", "region_type": "recommendation", "sort_order": 40},
    )
    region = region_response.json()

    block_response = client.post(
        f"{BASE}/regions/{region['region_code']}/blocks",
        json={
            "block_name": "主广告不应放推荐区",
            "block_type": "hero_banner",
            "sort_order": 10,
            "content": {},
            "layout": {},
        },
    )

    assert block_response.status_code == 422
    assert block_response.json()["detail"] == "block_type_not_allowed_for_region"


def test_update_region_and_block() -> None:
    region_response = client.post(
        f"{BASE}/regions",
        json={"region_name": "主体区域", "region_type": "main", "sort_order": 20},
    )
    region = region_response.json()

    update_region_response = client.patch(
        f"{BASE}/regions/{region['region_code']}",
        json={"region_name": "首页主体", "sort_order": 30},
    )

    assert update_region_response.status_code == 200
    assert update_region_response.json()["region_name"] == "首页主体"
    assert update_region_response.json()["sort_order"] == 30

    block_response = client.post(
        f"{BASE}/regions/{region['region_code']}/blocks",
        json={
            "block_name": "热卖商品",
            "block_type": "offer_shelf",
            "sort_order": 10,
            "content": {"source_ref": "shelf.hot"},
            "layout": {"columns": 4},
        },
    )
    block = block_response.json()

    update_block_response = client.patch(
        f"{BASE}/blocks/{block['block_code']}",
        json={
            "block_name": "热卖商品货架",
            "content": {"source_ref": "shelf.hot.updated"},
        },
    )

    assert update_block_response.status_code == 200
    updated = update_block_response.json()
    assert updated["block_name"] == "热卖商品货架"
    assert updated["content"]["source_ref"] == "shelf.hot.updated"
