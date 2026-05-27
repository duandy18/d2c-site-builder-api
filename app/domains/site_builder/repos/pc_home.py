from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.site_builder.models.pc_home import (
    SiteBuilderBlock,
    SiteBuilderPage,
    SiteBuilderRegion,
)


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


def list_blocks(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> list[SiteBuilderBlock]:
    statement = (
        select(SiteBuilderBlock)
        .where(
            SiteBuilderBlock.site_code == site_code,
            SiteBuilderBlock.surface_code == surface_code,
            SiteBuilderBlock.page_code == page_code,
        )
        .order_by(
            SiteBuilderBlock.region_code.asc(),
            SiteBuilderBlock.sort_order.asc(),
            SiteBuilderBlock.block_code.asc(),
        )
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


def get_block(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
    block_code: str,
) -> SiteBuilderBlock | None:
    statement = select(SiteBuilderBlock).where(
        SiteBuilderBlock.site_code == site_code,
        SiteBuilderBlock.surface_code == surface_code,
        SiteBuilderBlock.page_code == page_code,
        SiteBuilderBlock.block_code == block_code,
    )

    return session.scalars(statement).first()


def add_region(session: Session, region: SiteBuilderRegion) -> SiteBuilderRegion:
    session.add(region)
    session.flush()

    return region


def add_block(session: Session, block: SiteBuilderBlock) -> SiteBuilderBlock:
    session.add(block)
    session.flush()

    return block
