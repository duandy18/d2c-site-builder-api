from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.runtime_contract.contracts.page_contract import (
    RuntimePageContractResponse,
)
from app.domains.runtime_contract.services.page_contract import (
    build_runtime_page_contract,
)

router = APIRouter(prefix="/runtime/site-builder", tags=["runtime-page-contract"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get(
    "/sites/{site_code}/surfaces/{surface_code}/pages/{page_code}",
    response_model=RuntimePageContractResponse,
)
def get_runtime_page_contract(
    site_code: str,
    surface_code: str,
    page_code: str,
    session: SessionDep,
) -> RuntimePageContractResponse:
    return build_runtime_page_contract(session, site_code, surface_code, page_code)
