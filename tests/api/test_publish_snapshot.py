from fastapi.testclient import TestClient
from sqlalchemy import delete, update

from app.core.db import get_session
from app.domains.site_builder.models.pc_home import (
    SiteBuilderBlock,
    SiteBuilderPage,
    SiteBuilderPublishedPageSnapshot,
    SiteBuilderRegion,
)
from app.main import app

client = TestClient(app)

ADMIN_BASE = "/admin/site-builder/sites/default/surfaces/pc-web/pages"
RUNTIME_BASE = "/runtime/site-builder/sites/default/surfaces/pc-web/pages"


def _normalized_page_code(page_code: str) -> str:
    return page_code.replace("-", "_")


def _reset_page_state(page_code: str) -> None:
    normalized_page_code = _normalized_page_code(page_code)
    dependency = get_session()
    session = next(dependency)

    try:
        session.execute(
            delete(SiteBuilderPublishedPageSnapshot).where(
                SiteBuilderPublishedPageSnapshot.site_code == "default",
                SiteBuilderPublishedPageSnapshot.surface_code == "pc_web",
                SiteBuilderPublishedPageSnapshot.page_code == normalized_page_code,
            )
        )
        session.execute(
            delete(SiteBuilderBlock).where(
                SiteBuilderBlock.site_code == "default",
                SiteBuilderBlock.surface_code == "pc_web",
                SiteBuilderBlock.page_code == normalized_page_code,
            )
        )
        session.execute(
            delete(SiteBuilderRegion).where(
                SiteBuilderRegion.site_code == "default",
                SiteBuilderRegion.surface_code == "pc_web",
                SiteBuilderRegion.page_code == normalized_page_code,
            )
        )
        session.execute(
            update(SiteBuilderPage)
            .where(
                SiteBuilderPage.site_code == "default",
                SiteBuilderPage.surface_code == "pc_web",
                SiteBuilderPage.page_code == normalized_page_code,
            )
            .values(status="draft")
        )
        session.commit()
    finally:
        try:
            next(dependency)
        except StopIteration:
            pass


def _patch_slot(page_code: str, slot_code: str, content: dict[str, object]) -> None:
    response = client.patch(
        f"{ADMIN_BASE}/{page_code}/contents/{slot_code}",
        json={
            "content": content,
            "presentation": {},
        },
    )

    assert response.status_code == 200


def _make_image_matrix_ready(page_code: str, title: str) -> None:
    _patch_slot(
        page_code,
        "product.image_matrix.main",
        {"main_image": {"url": "https://example.com/main.jpg", "alt": "主图"}},
    )
    _patch_slot(
        page_code,
        "product.image_matrix.side_images",
        {
            "images": [
                {"url": "https://example.com/1.jpg"},
                {"url": "https://example.com/2.jpg"},
                {"url": "https://example.com/3.jpg"},
                {"url": "https://example.com/4.jpg"},
            ]
        },
    )
    _patch_slot(
        page_code,
        "product.summary.info",
        {
            "category": "猫砂",
            "title": title,
            "description": "低粉尘、高结团、除臭稳定。",
        },
    )
    _patch_slot(
        page_code,
        "product.price",
        {
            "sale_price": "¥39",
            "original_price": "¥49",
        },
    )
    _patch_slot(
        page_code,
        "product.cart_action",
        {
            "label": "加入购物车",
        },
    )


def _block_by_slot(payload: dict[str, object], slot_code: str) -> dict[str, object]:
    regions = payload["regions"]
    assert isinstance(regions, list)

    for region in regions:
        assert isinstance(region, dict)
        blocks = region["blocks"]
        assert isinstance(blocks, list)

        for block in blocks:
            assert isinstance(block, dict)
            if block["slot_code"] == slot_code:
                return block

    raise AssertionError(f"slot not found: {slot_code}")


def test_publish_rejects_blocked_page() -> None:
    page_code = "product-detail-image-matrix"
    _reset_page_state(page_code)

    response = client.post(
        f"{ADMIN_BASE}/{page_code}/publish",
        json={"published_by": "pytest"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "publish_readiness_blocked"


def test_publish_creates_snapshot_and_published_runtime_is_immutable() -> None:
    page_code = "product-detail-image-matrix"
    _reset_page_state(page_code)
    _make_image_matrix_ready(page_code, "第一次发布标题")

    publish_response = client.post(
        f"{ADMIN_BASE}/{page_code}/publish",
        json={"published_by": "pytest"},
    )

    assert publish_response.status_code == 200

    publish_payload = publish_response.json()
    assert publish_payload["publish_version"] == 1
    assert publish_payload["contract_version"] == "published-v1"
    assert publish_payload["published_by"] == "pytest"
    assert publish_payload["snapshot"]["status"] == "published"
    assert publish_payload["snapshot"]["contract_version"] == "published-v1"

    published_response = client.get(f"{RUNTIME_BASE}/{page_code}/published")
    assert published_response.status_code == 200

    published_payload = published_response.json()
    first_summary = _block_by_slot(published_payload, "product.summary.info")
    assert first_summary["content"]["title"] == "第一次发布标题"

    _patch_slot(
        page_code,
        "product.summary.info",
        {
            "category": "猫砂",
            "title": "第二次草稿标题",
            "description": "低粉尘、高结团、除臭稳定。",
        },
    )

    still_published_response = client.get(f"{RUNTIME_BASE}/{page_code}/published")
    assert still_published_response.status_code == 200

    still_published_payload = still_published_response.json()
    unchanged_summary = _block_by_slot(still_published_payload, "product.summary.info")
    assert unchanged_summary["content"]["title"] == "第一次发布标题"

    second_publish_response = client.post(
        f"{ADMIN_BASE}/{page_code}/publish",
        json={"published_by": "pytest"},
    )

    assert second_publish_response.status_code == 200
    assert second_publish_response.json()["publish_version"] == 2

    latest_published_response = client.get(f"{RUNTIME_BASE}/{page_code}/published")
    assert latest_published_response.status_code == 200

    latest_published_payload = latest_published_response.json()
    latest_summary = _block_by_slot(latest_published_payload, "product.summary.info")
    assert latest_summary["content"]["title"] == "第二次草稿标题"


def test_published_runtime_404_when_no_snapshot_exists() -> None:
    page_code = "product-detail-image-matrix"
    _reset_page_state(page_code)

    response = client.get(f"{RUNTIME_BASE}/{page_code}/published")

    assert response.status_code == 404
    assert response.json()["detail"] == "published_snapshot_not_found"


def test_publish_unknown_page_404() -> None:
    response = client.post(
        f"{ADMIN_BASE}/missing-page/publish",
        json={"published_by": "pytest"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "page_not_found"
