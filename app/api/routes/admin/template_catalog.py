from fastapi import APIRouter

from app.domains.site_builder.contracts.template_catalog import TemplateCatalogResponse
from app.domains.site_builder.services.template_catalog import list_template_catalog

router = APIRouter(prefix="/admin/site-builder", tags=["admin-site-builder"])


@router.get("/templates", response_model=TemplateCatalogResponse)
def get_site_builder_templates() -> TemplateCatalogResponse:
    return list_template_catalog()
