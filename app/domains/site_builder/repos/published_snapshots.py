from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.domains.site_builder.models.pc_home import SiteBuilderPublishedPageSnapshot


def get_current_snapshot(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> SiteBuilderPublishedPageSnapshot | None:
    statement = (
        select(SiteBuilderPublishedPageSnapshot)
        .where(
            SiteBuilderPublishedPageSnapshot.site_code == site_code,
            SiteBuilderPublishedPageSnapshot.surface_code == surface_code,
            SiteBuilderPublishedPageSnapshot.page_code == page_code,
            SiteBuilderPublishedPageSnapshot.is_current.is_(True),
        )
        .order_by(SiteBuilderPublishedPageSnapshot.publish_version.desc())
    )

    return session.scalars(statement).first()


def next_publish_version(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> int:
    statement = select(
        func.coalesce(func.max(SiteBuilderPublishedPageSnapshot.publish_version), 0)
    ).where(
        SiteBuilderPublishedPageSnapshot.site_code == site_code,
        SiteBuilderPublishedPageSnapshot.surface_code == surface_code,
        SiteBuilderPublishedPageSnapshot.page_code == page_code,
    )

    return int(session.scalar(statement) or 0) + 1


def clear_current_snapshots(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> None:
    statement = (
        update(SiteBuilderPublishedPageSnapshot)
        .where(
            SiteBuilderPublishedPageSnapshot.site_code == site_code,
            SiteBuilderPublishedPageSnapshot.surface_code == surface_code,
            SiteBuilderPublishedPageSnapshot.page_code == page_code,
            SiteBuilderPublishedPageSnapshot.is_current.is_(True),
        )
        .values(is_current=False)
    )

    session.execute(statement)


def add_snapshot(
    session: Session,
    snapshot: SiteBuilderPublishedPageSnapshot,
) -> SiteBuilderPublishedPageSnapshot:
    session.add(snapshot)
    session.flush()

    return snapshot
