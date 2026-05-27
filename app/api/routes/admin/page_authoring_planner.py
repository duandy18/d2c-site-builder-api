from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.page_planner import PagePlannerOptionsResponse
from app.domains.site_builder.services.page_planner import get_page_planner_options

router = APIRouter(
    prefix="/admin/site-builder/sites/{site_code}/surfaces/{surface_code}/pages/{page_code}",
    tags=["page-authoring-planner"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/planner-options", response_model=PagePlannerOptionsResponse)
def get_page_planner(
    site_code: str,
    surface_code: str,
    page_code: str,
    session: SessionDep,
) -> PagePlannerOptionsResponse:
    return get_page_planner_options(session, site_code, surface_code, page_code)
