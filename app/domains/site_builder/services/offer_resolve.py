import json
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.core.config import get_settings
from app.domains.site_builder.contracts.offer_resolve import ResolvedOfferDto


class OfferResolveUnavailableError(Exception):
    pass


def resolve_offer_from_d2c(offer_code: str) -> ResolvedOfferDto | None:
    normalized_offer_code = offer_code.strip()

    if not normalized_offer_code:
        return None

    settings = get_settings()
    url = (
        f"{settings.d2c_api_base_url.rstrip()}"
        f"/catalog/products/{quote(normalized_offer_code, safe='')}"
    )
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "X-Site-Builder-Client": "d2c-site-builder-api",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=settings.d2c_api_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise OfferResolveUnavailableError("d2c_offer_resolve_unavailable") from exc
    except (OSError, URLError, json.JSONDecodeError) as exc:
        raise OfferResolveUnavailableError("d2c_offer_resolve_unavailable") from exc

    return _catalog_product_to_offer(payload)


def _catalog_product_to_offer(payload: dict[str, object]) -> ResolvedOfferDto:
    product_id = _required_text(payload, "product_id")
    price_cents = _required_int(payload, "price_cents")
    currency = _optional_text(payload, "currency") or "USD"

    return ResolvedOfferDto(
        offer_code=product_id,
        title=_required_text(payload, "name"),
        category=_optional_text(payload, "category") or "全部商品",
        description=_optional_text(payload, "description") or "",
        price_cents=price_cents,
        currency=currency,
        display_price=_format_display_price(price_cents, currency),
        image_url=_optional_text(payload, "image_url"),
        status=_optional_text(payload, "status") or "active",
        stock_status=_optional_text(payload, "stock_status") or "in_stock",
    )


def _required_text(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)

    if isinstance(value, str) and value.strip():
        return value.strip()

    raise OfferResolveUnavailableError("d2c_offer_resolve_invalid_payload")


def _optional_text(payload: dict[str, object], key: str) -> str | None:
    value = payload.get(key)

    if isinstance(value, str) and value.strip():
        return value.strip()

    return None


def _required_int(payload: dict[str, object], key: str) -> int:
    value = payload.get(key)

    if isinstance(value, int) and value >= 0:
        return value

    raise OfferResolveUnavailableError("d2c_offer_resolve_invalid_payload")


def _format_display_price(price_cents: int, currency: str) -> str:
    amount = Decimal(price_cents) / Decimal(100)

    if currency == "USD":
        return f"${amount:.2f}"

    return f"{currency} {amount:.2f}"
