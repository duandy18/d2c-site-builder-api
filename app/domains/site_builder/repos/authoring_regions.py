from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.site_builder.models.pc_home import SiteBuilderRegion


def list_regions(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> list[SiteBuilderRegion]:
    statement = (
        select(SiteBuilderRegion)
        .where(
            SiteBuilderRegion.site_code == site_code,
            SiteBuilderRegion.surface_code == surface_code,
            SiteBuilderRegion.page_code == page_code,
        )
        .order_by(SiteBuilderRegion.sort_order.asc(), SiteBuilderRegion.region_code.asc())
    )

    return list(session.scalars(statement).all())


def get_region(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
    region_code: str,
) -> SiteBuilderRegion | None:
    statement = select(SiteBuilderRegion).where(
        SiteBuilderRegion.site_code == site_code,
        SiteBuilderRegion.surface_code == surface_code,
        SiteBuilderRegion.page_code == page_code,
        SiteBuilderRegion.region_code == region_code,
    )

    return session.scalars(statement).first()


def add_region(session: Session, region: SiteBuilderRegion) -> SiteBuilderRegion:
    session.add(region)
    session.flush()

    return region
