from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.page_content import (
    PageContentFormResponse,
    SlotContentResponse,
    UpdateSlotContentRequest,
)
from app.domains.site_builder.services.page_content import (
    build_page_content_form,
    update_slot_content,
)

router = APIRouter(
    prefix="/admin/site-builder/sites/{site_code}/surfaces/{surface_code}/pages/{page_code}",
    tags=["page-authoring-content"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/content-form", response_model=PageContentFormResponse)
def get_page_content_form(
    site_code: str,
    surface_code: str,
    page_code: str,
    session: SessionDep,
) -> PageContentFormResponse:
    return build_page_content_form(session, site_code, surface_code, page_code)


@router.patch("/contents/{slot_code}", response_model=SlotContentResponse)
def patch_page_slot_content(
    site_code: str,
    surface_code: str,
    page_code: str,
    slot_code: str,
    request: UpdateSlotContentRequest,
    session: SessionDep,
) -> SlotContentResponse:
    return update_slot_content(
        session,
        site_code,
        surface_code,
        page_code,
        slot_code,
        request,
    )
