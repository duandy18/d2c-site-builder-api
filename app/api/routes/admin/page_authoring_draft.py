from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.page_draft import PageDraftResponse
from app.domains.site_builder.services.page_draft import build_page_draft

router = APIRouter(
    prefix="/admin/site-builder/sites/{site_code}/surfaces/{surface_code}/pages/{page_code}",
    tags=["page-authoring-draft"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/draft", response_model=PageDraftResponse)
def get_page_draft(
    site_code: str,
    surface_code: str,
    page_code: str,
    session: SessionDep,
) -> PageDraftResponse:
    return build_page_draft(session, site_code, surface_code, page_code)
