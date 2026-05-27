from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.site_builder.models.pc_home import SiteBuilderBlock


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


def add_block(session: Session, block: SiteBuilderBlock) -> SiteBuilderBlock:
    session.add(block)
    session.flush()

    return block
