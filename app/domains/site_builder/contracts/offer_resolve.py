from pydantic import BaseModel, Field


class ResolvedOfferDto(BaseModel):
    offer_code: str
    title: str
    category: str
    description: str
    price_cents: int = Field(..., ge=0)
    currency: str
    display_price: str
    image_url: str | None = None
    status: str
    stock_status: str


class OfferResolveResponse(BaseModel):
    offer: ResolvedOfferDto
