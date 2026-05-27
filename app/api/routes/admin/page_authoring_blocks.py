from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.page_authoring_common import PageAuthoringBlockDto
from app.domains.site_builder.contracts.page_blocks import (
    CreateBlockRequest,
    UpdateBlockRequest,
)
from app.domains.site_builder.services.page_blocks import (
    create_page_block,
    update_page_block,
)

router = APIRouter(
    prefix="/admin/site-builder/sites/{site_code}/surfaces/{surface_code}/pages/{page_code}",
    tags=["page-authoring-blocks"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/regions/{region_code}/blocks", response_model=PageAuthoringBlockDto)
def create_block(
    site_code: str,
    surface_code: str,
    page_code: str,
    region_code: str,
    request: CreateBlockRequest,
    session: SessionDep,
) -> PageAuthoringBlockDto:
    return create_page_block(
        session,
        site_code,
        surface_code,
        page_code,
        region_code,
        request,
    )


@router.patch("/blocks/{block_code}", response_model=PageAuthoringBlockDto)
def update_block(
    site_code: str,
    surface_code: str,
    page_code: str,
    block_code: str,
    request: UpdateBlockRequest,
    session: SessionDep,
) -> PageAuthoringBlockDto:
    return update_page_block(
        session,
        site_code,
        surface_code,
        page_code,
        block_code,
        request,
    )
