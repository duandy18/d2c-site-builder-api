from dataclasses import dataclass

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domains.site_builder.repos.authoring_pages import get_page
from app.domains.site_builder.services.page_authoring_capabilities import (
    require_template_name,
)


@dataclass(frozen=True)
class PageAuthoringContext:
    site_code: str
    surface_code: str
    page_code: str
    page_title: str
    template_key: str
    template_name: str


def normalize_surface_code(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def normalize_page_code(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def require_page_context(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> PageAuthoringContext:
    normalized_surface_code = normalize_surface_code(surface_code)
    normalized_page_code = normalize_page_code(page_code)

    page = get_page(
        session,
        site_code,
        normalized_surface_code,
        normalized_page_code,
    )

    if not page:
        raise HTTPException(status_code=404, detail="page_not_found")

    return PageAuthoringContext(
        site_code=page.site_code,
        surface_code=page.surface_code,
        page_code=page.page_code,
        page_title=page.page_title,
        template_key=page.template_key,
        template_name=require_template_name(session, page.template_key),
    )
