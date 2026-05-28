from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.site_builder.models.pc_home import (
    SiteBuilderTemplate,
    SiteBuilderTemplateRegion,
    SiteBuilderTemplateSlot,
)


def get_template(session: Session, template_key: str) -> SiteBuilderTemplate | None:
    statement = select(SiteBuilderTemplate).where(
        SiteBuilderTemplate.template_key == template_key,
        SiteBuilderTemplate.status == "active",
    )

    return session.scalars(statement).first()


def list_templates(session: Session) -> list[SiteBuilderTemplate]:
    statement = (
        select(SiteBuilderTemplate)
        .where(SiteBuilderTemplate.status == "active")
        .order_by(
            SiteBuilderTemplate.surface_code.asc(),
            SiteBuilderTemplate.sort_order.asc(),
            SiteBuilderTemplate.template_key.asc(),
        )
    )

    return list(session.scalars(statement).all())


def list_template_regions(
    session: Session,
    template_key: str,
) -> list[SiteBuilderTemplateRegion]:
    statement = (
        select(SiteBuilderTemplateRegion)
        .where(
            SiteBuilderTemplateRegion.template_key == template_key,
            SiteBuilderTemplateRegion.status == "active",
        )
        .order_by(
            SiteBuilderTemplateRegion.sort_order.asc(),
            SiteBuilderTemplateRegion.template_region_code.asc(),
        )
    )

    return list(session.scalars(statement).all())


def list_template_slots(
    session: Session,
    template_key: str,
) -> list[SiteBuilderTemplateSlot]:
    statement = (
        select(SiteBuilderTemplateSlot)
        .where(
            SiteBuilderTemplateSlot.template_key == template_key,
            SiteBuilderTemplateSlot.status == "active",
        )
        .order_by(
            SiteBuilderTemplateSlot.template_region_code.asc(),
            SiteBuilderTemplateSlot.sort_order.asc(),
            SiteBuilderTemplateSlot.slot_code.asc(),
        )
    )

    return list(session.scalars(statement).all())


def list_template_slots_for_region(
    session: Session,
    template_key: str,
    template_region_code: str,
) -> list[SiteBuilderTemplateSlot]:
    statement = (
        select(SiteBuilderTemplateSlot)
        .where(
            SiteBuilderTemplateSlot.template_key == template_key,
            SiteBuilderTemplateSlot.template_region_code == template_region_code,
            SiteBuilderTemplateSlot.status == "active",
        )
        .order_by(
            SiteBuilderTemplateSlot.sort_order.asc(),
            SiteBuilderTemplateSlot.slot_code.asc(),
        )
    )

    return list(session.scalars(statement).all())


def get_template_slot(
    session: Session,
    template_key: str,
    slot_code: str,
) -> SiteBuilderTemplateSlot | None:
    statement = select(SiteBuilderTemplateSlot).where(
        SiteBuilderTemplateSlot.template_key == template_key,
        SiteBuilderTemplateSlot.slot_code == slot_code,
        SiteBuilderTemplateSlot.status == "active",
    )

    return session.scalars(statement).first()
