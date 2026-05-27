from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.pc_home import (
    CreateBlockRequest,
    CreateRegionRequest,
    PcHomeBlockDto,
    PcHomeDraftResponse,
    PcHomePlannerOptionsResponse,
    PcHomeRegionDto,
    UpdateBlockRequest,
    UpdateRegionRequest,
)
from app.domains.site_builder.services.pc_home import (
    build_home_draft,
    create_block,
    create_region,
    get_planner_options,
    update_block,
    update_region,
)

router = APIRouter(
    prefix="/admin/site-builder/sites/default/surfaces/pc-web/pages/home",
    tags=["pc-home-authoring"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/draft", response_model=PcHomeDraftResponse)
def get_pc_home_draft(session: SessionDep) -> PcHomeDraftResponse:
    return build_home_draft(session)


@router.get("/planner-options", response_model=PcHomePlannerOptionsResponse)
def get_pc_home_planner_options() -> PcHomePlannerOptionsResponse:
    return get_planner_options()


@router.post("/regions", response_model=PcHomeRegionDto)
def create_pc_home_region(
    request: CreateRegionRequest,
    session: SessionDep,
) -> PcHomeRegionDto:
    return create_region(session, request)


@router.patch("/regions/{region_code}", response_model=PcHomeRegionDto)
def update_pc_home_region(
    region_code: str,
    request: UpdateRegionRequest,
    session: SessionDep,
) -> PcHomeRegionDto:
    return update_region(session, region_code, request)


@router.post("/regions/{region_code}/blocks", response_model=PcHomeBlockDto)
def create_pc_home_block(
    region_code: str,
    request: CreateBlockRequest,
    session: SessionDep,
) -> PcHomeBlockDto:
    return create_block(session, region_code, request)


@router.patch("/blocks/{block_code}", response_model=PcHomeBlockDto)
def update_pc_home_block(
    block_code: str,
    request: UpdateBlockRequest,
    session: SessionDep,
) -> PcHomeBlockDto:
    return update_block(session, block_code, request)
