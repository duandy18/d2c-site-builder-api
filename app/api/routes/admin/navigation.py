from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.admin_pages import SiteBuilderNavigationResponse
from app.domains.site_builder.repos.admin_pages import list_active_admin_pages
from app.domains.site_builder.services.admin_navigation import build_navigation_response

router = APIRouter(prefix="/admin/site-builder", tags=["admin-navigation"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/navigation", response_model=SiteBuilderNavigationResponse)
def get_site_builder_navigation(
    session: SessionDep,
) -> SiteBuilderNavigationResponse:
    pages = list_active_admin_pages(session)

    return build_navigation_response(pages)
