from fastapi import APIRouter, HTTPException, status

from app.domains.site_builder.contracts.offer_resolve import OfferResolveResponse
from app.domains.site_builder.services.offer_resolve import (
    OfferResolveUnavailableError,
    resolve_offer_from_d2c,
)

router = APIRouter(prefix="/admin/site-builder/offers", tags=["offer-resolve"])


@router.get("/{offer_code}/resolve", response_model=OfferResolveResponse)
def resolve_offer(offer_code: str) -> OfferResolveResponse:
    try:
        offer = resolve_offer_from_d2c(offer_code)
    except OfferResolveUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    if offer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="offer_not_found",
        )

    return OfferResolveResponse(offer=offer)
