from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AdminPageStatus = Literal["connected", "planned", "disabled"]


class SiteBuilderAdminPageDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page_code: str
    title: str
    parent_code: str | None
    level: int
    route_path: str
    component_key: str
    show_in_sidebar: bool
    sort_order: int
    status: AdminPageStatus
    is_active: bool
    children: list["SiteBuilderAdminPageDto"] = Field(default_factory=list)


class SiteBuilderNavigationResponse(BaseModel):
    app_code: str
    pages: list[SiteBuilderAdminPageDto]


SiteBuilderAdminPageDto.model_rebuild()
