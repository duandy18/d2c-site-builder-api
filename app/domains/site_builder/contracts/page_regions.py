from typing import Literal

from pydantic import BaseModel


class CreateRegionRequest(BaseModel):
    template_region_code: str
    region_name: str | None = None
    sort_order: int | None = None


class UpdateRegionRequest(BaseModel):
    region_name: str | None = None
    sort_order: int | None = None
    status: Literal["active", "disabled"] | None = None
