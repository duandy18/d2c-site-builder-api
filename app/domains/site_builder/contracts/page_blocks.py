from typing import Literal

from pydantic import BaseModel, Field

from app.domains.site_builder.contracts.page_authoring_common import JsonRecord


class CreateBlockRequest(BaseModel):
    block_name: str
    block_type: str
    sort_order: int = 100
    content: JsonRecord = Field(default_factory=dict)
    presentation: JsonRecord = Field(default_factory=dict)


class UpdateBlockRequest(BaseModel):
    block_name: str | None = None
    sort_order: int | None = None
    content: JsonRecord | None = None
    presentation: JsonRecord | None = None
    status: Literal["active", "disabled"] | None = None
