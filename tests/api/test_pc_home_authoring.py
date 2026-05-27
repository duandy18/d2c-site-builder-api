from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_pc_home_draft_starts_empty() -> None:
    response = client.get("/admin/site-builder/sites/default/surfaces/pc-web/pages/home/draft")

    assert response.status_code == 200
    assert response.json()["site_code"] == "default"
    assert response.json()["surface_code"] == "pc_web"
    assert response.json()["page_code"] == "home"
    assert response.json()["regions"] == []


def test_pc_home_planner_options() -> None:
    response = client.get(
        "/admin/site-builder/sites/default/surfaces/pc-web/pages/home/planner-options"
    )

    assert response.status_code == 200
    payload = response.json()

    assert {item["value"] for item in payload["allowed_region_types"]} >= {"hero", "main"}
    assert {item["value"] for item in payload["allowed_block_types"]} >= {
        "hero_banner",
        "offer_shelf",
    }


def test_create_region_and_block() -> None:
    region_response = client.post(
        "/admin/site-builder/sites/default/surfaces/pc-web/pages/home/regions",
        json={"region_name": "头图区域", "region_type": "hero", "sort_order": 10},
    )

    assert region_response.status_code == 200
    region = region_response.json()
    assert region["region_code"] == "home.hero"
    assert region["region_name"] == "头图区域"
    assert region["blocks"] == []

    block_response = client.post(
        (
            "/admin/site-builder/sites/default/surfaces/pc-web/pages/home"
            f"/regions/{region['region_code']}/blocks"
        ),
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
    assert block["block_code"] == "home.hero.hero-banner"
    assert block["renderer_key"] == "pc_web.hero_banner"

    draft_response = client.get(
        "/admin/site-builder/sites/default/surfaces/pc-web/pages/home/draft"
    )
    assert draft_response.status_code == 200

    draft = draft_response.json()
    assert draft["regions"][0]["region_code"] == "home.hero"
    assert draft["regions"][0]["blocks"][0]["block_code"] == "home.hero.hero-banner"


def test_update_region_and_block() -> None:
    region_response = client.post(
        "/admin/site-builder/sites/default/surfaces/pc-web/pages/home/regions",
        json={"region_name": "主体区域", "region_type": "main", "sort_order": 20},
    )
    region = region_response.json()

    update_region_response = client.patch(
        (
            "/admin/site-builder/sites/default/surfaces/pc-web/pages/home"
            f"/regions/{region['region_code']}"
        ),
        json={"region_name": "首页主体", "sort_order": 30},
    )

    assert update_region_response.status_code == 200
    assert update_region_response.json()["region_name"] == "首页主体"
    assert update_region_response.json()["sort_order"] == 30

    block_response = client.post(
        (
            "/admin/site-builder/sites/default/surfaces/pc-web/pages/home"
            f"/regions/{region['region_code']}/blocks"
        ),
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
        (
            "/admin/site-builder/sites/default/surfaces/pc-web/pages/home"
            f"/blocks/{block['block_code']}"
        ),
        json={
            "block_name": "热卖商品货架",
            "content": {"source_ref": "shelf.hot.updated"},
        },
    )

    assert update_block_response.status_code == 200
    updated = update_block_response.json()
    assert updated["block_name"] == "热卖商品货架"
    assert updated["content"]["source_ref"] == "shelf.hot.updated"
