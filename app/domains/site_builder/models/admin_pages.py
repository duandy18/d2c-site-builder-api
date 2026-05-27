from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SiteBuilderAdminPage(Base):
    __tablename__ = "sb_admin_pages"
    __table_args__ = (
        Index(
            "ix_sb_admin_pages_parent_sort",
            "parent_code",
            "sort_order",
            "page_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    page_code: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    parent_code: Mapped[str | None] = mapped_column(String(160), nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    route_path: Mapped[str] = mapped_column(String(240), unique=True, nullable=False)
    component_key: Mapped[str] = mapped_column(String(180), nullable=False)
    show_in_sidebar: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("100"),
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'planned'"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
