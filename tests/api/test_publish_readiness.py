from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.db import get_session
from app.domains.site_builder.models.pc_home import SiteBuilderBlock
from app.main import app

client = TestClient(app)

BASE = "/admin/site-builder/sites/default/surfaces/pc-web/pages"


def _normalized_page_code(page_code: str) -> str:
    return page_code.replace("-", "_")


def _reset_page_blocks(page_code: str) -> None:
    dependency = get_session()
    session = next(dependency)

    try:
        session.execute(
            delete(SiteBuilderBlock).where(
                SiteBuilderBlock.site_code == "default",
                SiteBuilderBlock.surface_code == "pc_web",
                SiteBuilderBlock.page_code == _normalized_page_code(page_code),
            )
        )
        session.commit()
    finally:
        try:
            next(dependency)
        except StopIteration:
            pass


def _patch_slot(page_code: str, slot_code: str, content: dict[str, object]) -> None:
    response = client.patch(
        f"{BASE}/{page_code}/contents/{slot_code}",
        json={
            "content": content,
            "presentation": {},
        },
    )

    assert response.status_code == 200


def test_publish_readiness_reports_missing_required_slots() -> None:
    page_code = "product-detail-image-matrix"
    _reset_page_blocks(page_code)

    response = client.get(f"{BASE}/{page_code}/publish-readiness")

    assert response.status_code == 200

    payload = response.json()
    assert payload["page_code"] == "product_detail_image_matrix"
    assert payload["template_key"] == "pc_product_detail_image_matrix_v1"
    assert payload["ready"] is False
    assert payload["status"] == "blocked"
    assert payload["summary"]["issue_count"] >= 1
    assert payload["summary"]["missing_required_slot_count"] >= 1

    issues = payload["issues"]
    assert any(
        issue["code"] == "missing_required_field"
        and issue["slot_code"] == "product.image_matrix.main"
        and issue["field_key"] == "main_image"
        for issue in issues
    )
    assert any(
        issue["code"] == "image_matrix_side_images_min_4"
        and issue["slot_code"] == "product.image_matrix.side_images"
        for issue in issues
    )


def test_publish_readiness_passes_when_required_slots_are_complete() -> None:
    page_code = "product-detail-image-matrix"
    _reset_page_blocks(page_code)

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
            "title": "豆腐混合猫砂 6L",
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

    response = client.get(f"{BASE}/{page_code}/publish-readiness")

    assert response.status_code == 200

    payload = response.json()
    error_codes = {issue["code"] for issue in payload["issues"] if issue["level"] == "error"}
    warning_codes = {issue["code"] for issue in payload["issues"] if issue["level"] == "warning"}

    assert payload["ready"] is True
    assert payload["status"] == "ready"
    assert error_codes == set()
    assert "image_matrix_side_images_recommend_6" in warning_codes
    assert payload["summary"]["warning_count"] == 1


def test_publish_readiness_404_for_unknown_page() -> None:
    response = client.get(f"{BASE}/missing-page/publish-readiness")

    assert response.status_code == 404
    assert response.json()["detail"] == "page_not_found"
