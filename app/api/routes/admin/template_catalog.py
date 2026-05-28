from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.domains.site_builder.contracts.template_catalog import TemplateCatalogResponse
from app.domains.site_builder.services.template_catalog import list_template_catalog

router = APIRouter(prefix="/admin/site-builder", tags=["admin-site-builder"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/templates", response_model=TemplateCatalogResponse)
def get_site_builder_templates(session: SessionDep) -> TemplateCatalogResponse:
    return list_template_catalog(session)
