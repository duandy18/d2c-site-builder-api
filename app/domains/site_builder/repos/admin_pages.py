from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.site_builder.models.admin_pages import SiteBuilderAdminPage


def list_active_admin_pages(session: Session) -> list[SiteBuilderAdminPage]:
    statement = (
        select(SiteBuilderAdminPage)
        .where(SiteBuilderAdminPage.is_active.is_(True))
        .order_by(
            SiteBuilderAdminPage.level.asc(),
            SiteBuilderAdminPage.parent_code.asc().nullsfirst(),
            SiteBuilderAdminPage.sort_order.asc(),
            SiteBuilderAdminPage.page_code.asc(),
        )
    )

    return list(session.scalars(statement).all())
