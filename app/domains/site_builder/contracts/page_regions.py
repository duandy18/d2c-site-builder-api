from typing import Literal

from pydantic import BaseModel


class CreateRegionRequest(BaseModel):
    region_name: str
    region_type: str
    sort_order: int = 100


class UpdateRegionRequest(BaseModel):
    region_name: str | None = None
    sort_order: int | None = None
    status: Literal["active", "disabled"] | None = None
