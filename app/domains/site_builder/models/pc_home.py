from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SiteBuilderSite(Base):
    __tablename__ = "sb_sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    site_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'active'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class SiteBuilderSurface(Base):
    __tablename__ = "sb_surfaces"
    __table_args__ = (
        UniqueConstraint("site_code", "surface_code", name="uq_sb_surfaces_site_surface"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_code: Mapped[str] = mapped_column(String(80), nullable=False)
    surface_code: Mapped[str] = mapped_column(String(40), nullable=False)
    surface_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'active'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class SiteBuilderTemplate(Base):
    __tablename__ = "sb_templates"
    __table_args__ = (
        UniqueConstraint("template_key", name="uq_sb_templates_key"),
        UniqueConstraint("surface_code", "page_code", name="uq_sb_templates_surface_page"),
        Index("ix_sb_templates_surface_sort", "surface_code", "sort_order", "template_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_key: Mapped[str] = mapped_column(String(120), nullable=False)
    template_name: Mapped[str] = mapped_column(String(160), nullable=False)
    surface_code: Mapped[str] = mapped_column(String(40), nullable=False)
    page_code: Mapped[str] = mapped_column(String(80), nullable=False)
    template_version: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'active'"))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("100"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class SiteBuilderTemplateRegion(Base):
    __tablename__ = "sb_template_regions"
    __table_args__ = (
        UniqueConstraint("template_key", "template_region_code", name="uq_sb_tpl_regions_key"),
        Index("ix_sb_tpl_regions_sort", "template_key", "sort_order", "template_region_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_key: Mapped[str] = mapped_column(
        String(120),
        ForeignKey("sb_templates.template_key", ondelete="CASCADE"),
        nullable=False,
    )
    template_region_code: Mapped[str] = mapped_column(String(80), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    required: Mapped[bool] = mapped_column(nullable=False, server_default=text("false"))
    default_region_name: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("100"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'active'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class SiteBuilderTemplateSlot(Base):
    __tablename__ = "sb_template_slots"
    __table_args__ = (
        UniqueConstraint("template_key", "slot_code", name="uq_sb_tpl_slots_key"),
        Index(
            "ix_sb_tpl_slots_region_sort",
            "template_key",
            "template_region_code",
            "sort_order",
            "slot_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_key: Mapped[str] = mapped_column(
        String(120),
        ForeignKey("sb_templates.template_key", ondelete="CASCADE"),
        nullable=False,
    )
    template_region_code: Mapped[str] = mapped_column(String(80), nullable=False)
    slot_code: Mapped[str] = mapped_column(String(120), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    block_type: Mapped[str] = mapped_column(String(80), nullable=False)
    renderer_key: Mapped[str] = mapped_column(String(120), nullable=False)
    required: Mapped[bool] = mapped_column(nullable=False, server_default=text("false"))
    default_block_name: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("100"))
    content_schema_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, server_default=text("'{}'::json")
    )
    presentation_schema_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, server_default=text("'{}'::json")
    )
    default_content_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, server_default=text("'{}'::json")
    )
    default_presentation_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, server_default=text("'{}'::json")
    )
    validation_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, server_default=text("'{}'::json")
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'active'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class SiteBuilderPage(Base):
    __tablename__ = "sb_pages"
    __table_args__ = (
        UniqueConstraint("site_code", "surface_code", "page_code", name="uq_sb_pages_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_code: Mapped[str] = mapped_column(String(80), nullable=False)
    surface_code: Mapped[str] = mapped_column(String(40), nullable=False)
    page_code: Mapped[str] = mapped_column(String(80), nullable=False)
    page_title: Mapped[str] = mapped_column(String(120), nullable=False)
    template_key: Mapped[str] = mapped_column(
        String(120),
        ForeignKey("sb_templates.template_key"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'draft'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class SiteBuilderRegion(Base):
    __tablename__ = "sb_regions"
    __table_args__ = (
        UniqueConstraint(
            "site_code", "surface_code", "page_code", "region_code", name="uq_sb_regions_key"
        ),
        Index(
            "ix_sb_regions_page_sort",
            "site_code",
            "surface_code",
            "page_code",
            "sort_order",
            "region_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_code: Mapped[str] = mapped_column(String(80), nullable=False)
    surface_code: Mapped[str] = mapped_column(String(40), nullable=False)
    page_code: Mapped[str] = mapped_column(String(80), nullable=False)
    region_code: Mapped[str] = mapped_column(String(120), nullable=False)
    region_name: Mapped[str] = mapped_column(String(120), nullable=False)
    region_type: Mapped[str] = mapped_column(String(60), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("100"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'active'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class SiteBuilderBlock(Base):
    __tablename__ = "sb_blocks"
    __table_args__ = (
        UniqueConstraint(
            "site_code", "surface_code", "page_code", "block_code", name="uq_sb_blocks_key"
        ),
        Index(
            "ix_sb_blocks_region_sort",
            "site_code",
            "surface_code",
            "page_code",
            "region_code",
            "sort_order",
            "block_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_code: Mapped[str] = mapped_column(String(80), nullable=False)
    surface_code: Mapped[str] = mapped_column(String(40), nullable=False)
    page_code: Mapped[str] = mapped_column(String(80), nullable=False)
    region_code: Mapped[str] = mapped_column(String(120), nullable=False)
    block_code: Mapped[str] = mapped_column(String(160), nullable=False)
    block_name: Mapped[str] = mapped_column(String(120), nullable=False)
    block_type: Mapped[str] = mapped_column(String(60), nullable=False)
    renderer_key: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("100"))
    content_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, server_default=text("'{}'::json")
    )
    presentation_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, server_default=text("'{}'::json")
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'active'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
