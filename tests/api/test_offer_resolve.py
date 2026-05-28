from fastapi.testclient import TestClient

from app.api.routes.admin import offer_resolve as offer_resolve_route
from app.domains.site_builder.contracts.offer_resolve import ResolvedOfferDto
from app.main import app

client = TestClient(app)


def _offer(offer_code: str) -> ResolvedOfferDto:
    return ResolvedOfferDto(
        offer_code=offer_code,
        title="豆腐猫砂 6L",
        category="猫砂",
        description="低粉尘",
        price_cents=1099,
        currency="USD",
        display_price="$10.99",
        image_url=None,
        status="active",
        stock_status="in_stock",
    )


def test_offer_resolve_returns_offer(monkeypatch) -> None:
    monkeypatch.setattr(
        offer_resolve_route,
        "resolve_offer_from_d2c",
        lambda offer_code: _offer(offer_code),
    )

    response = client.get("/admin/site-builder/offers/offer.cat_litter.tofu_6l/resolve")

    assert response.status_code == 200
    assert response.json()["offer"]["offer_code"] == "offer.cat_litter.tofu_6l"
    assert response.json()["offer"]["price_cents"] == 1099
    assert response.json()["offer"]["display_price"] == "$10.99"


def test_offer_resolve_404_when_offer_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        offer_resolve_route,
        "resolve_offer_from_d2c",
        lambda _offer_code: None,
    )

    response = client.get("/admin/site-builder/offers/missing-offer/resolve")

    assert response.status_code == 404
    assert response.json()["detail"] == "offer_not_found"
