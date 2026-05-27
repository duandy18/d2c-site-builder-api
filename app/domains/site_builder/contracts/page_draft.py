from pydantic import BaseModel

from app.domains.site_builder.contracts.page_authoring_common import PageAuthoringRegionDto


class PageDraftResponse(BaseModel):
    site_code: str
    surface_code: str
    page_code: str
    page_title: str
    regions: list[PageAuthoringRegionDto]
