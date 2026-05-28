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
    assert payload["template_key"] == "pc_home_simple_shop_v1"
    assert isinstance(payload["regions"], list)


def test_page_planner_options_include_template_regions() -> None:
    response = client.get(f"{BASE}/planner-options")

    assert response.status_code == 200
    payload = response.json()

    assert payload["template_key"] == "pc_home_simple_shop_v1"
    assert payload["template_name"] == "极简商品型首页"

    template_regions = {item["template_region_code"]: item for item in payload["template_regions"]}
    assert set(template_regions) >= {
        "home.header",
        "home.product_collection",
        "home.hero",
        "home.campaign",
        "home.product_category",
        "home.product_grid",
        "home.service",
        "home.legal_footer",
    }
    assert template_regions["home.campaign"]["required"] is True
    assert "campaign_banner" in template_regions["home.campaign"]["allowed_block_types"]
    assert "product_grid" in template_regions["home.product_grid"]["allowed_block_types"]

    assert {item["value"] for item in payload["allowed_block_types"]} >= {
        "campaign_banner",
        "product_grid",
        "product_category_nav",
    }


def test_create_template_region_and_block() -> None:
    region = _ensure_region("home.campaign", "首页广告位", 40)

    assert region["region_code"] == "home.home.campaign"
    assert region["template_region_code"] == "home.campaign"
    assert region["region_name"]
    assert "blocks" in region

    block_response = client.post(
        f"{BASE}/regions/{region['region_code']}/blocks",
        json={
            "block_name": "首页广告位",
            "block_type": "campaign_banner",
            "sort_order": 10,
            "content": {
                "label": "大促活动",
                "title": "满 99 减 20",
                "subtitle": "猫砂猫粮组合优惠",
            },
            "presentation": {"tone": "dark"},
        },
    )

    assert block_response.status_code == 200
    block = block_response.json()
    assert block["block_code"].startswith("home.home.campaign.campaign_banner")
    assert block["renderer_key"] == "pc_web.campaign_banner"
    assert block["presentation"]["tone"] == "dark"


def test_create_duplicate_template_region_is_rejected() -> None:
    region = _ensure_region("home.product_grid", "商品列表")
    assert region["template_region_code"] == "home.product_grid"

    second_response = client.post(
        f"{BASE}/regions",
        json={"template_region_code": "home.product_grid", "region_name": "重复商品列表"},
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "template_region_already_enabled"


def test_create_block_rejects_invalid_template_region_block_rule() -> None:
    region = _ensure_region("home.service", "服务承诺")

    block_response = client.post(
        f"{BASE}/regions/{region['region_code']}/blocks",
        json={
            "block_name": "广告不应放服务承诺",
            "block_type": "campaign_banner",
            "sort_order": 10,
            "content": {
                "title": "错误广告",
            },
            "presentation": {},
        },
    )

    assert block_response.status_code == 422
    assert block_response.json()["detail"] == "block_type_not_allowed_for_region"


def test_update_region_and_block() -> None:
    region = _ensure_region("home.product_grid", "商品列表")

    update_region_response = client.patch(
        f"{BASE}/regions/{region['region_code']}",
        json={"region_name": "首页商品列表", "sort_order": 60},
    )

    assert update_region_response.status_code == 200
    assert update_region_response.json()["region_name"] == "首页商品列表"
    assert update_region_response.json()["sort_order"] == 60

    block_response = client.post(
        f"{BASE}/regions/{region['region_code']}/blocks",
        json={
            "block_name": "首页商品列表",
            "block_type": "product_grid",
            "sort_order": 10,
            "content": {
                "source": {"type": "manual", "ref": "home_products"},
                "products": [],
            },
            "presentation": {"columns_pc": 3},
        },
    )
    assert block_response.status_code == 200

    block = block_response.json()

    update_block_response = client.patch(
        f"{BASE}/blocks/{block['block_code']}",
        json={
            "block_name": "首页商品网格",
            "content": {
                "source": {"type": "manual", "ref": "updated_home_products"},
                "products": [],
            },
            "presentation": {"columns_pc": 3, "columns_mobile": 2},
        },
    )

    assert update_block_response.status_code == 200
    updated = update_block_response.json()
    assert updated["block_name"] == "首页商品网格"
    assert updated["content"]["source"]["ref"] == "updated_home_products"
    assert updated["presentation"]["columns_mobile"] == 2
