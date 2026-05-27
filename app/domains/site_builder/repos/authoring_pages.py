from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.site_builder.models.pc_home import SiteBuilderPage


def get_page(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> SiteBuilderPage | None:
    statement = select(SiteBuilderPage).where(
        SiteBuilderPage.site_code == site_code,
        SiteBuilderPage.surface_code == surface_code,
        SiteBuilderPage.page_code == page_code,
    )

    return session.scalars(statement).first()
