"""add pc web home authoring tables

Revision ID: 0003_pc_home
Revises: 0002_admin_pages
Create Date: 2026-05-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_pc_home"
down_revision: str | None = "0002_admin_pages"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sb_sites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_code", sa.String(length=80), nullable=False),
        sa.Column("site_name", sa.String(length=120), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("status IN ('active', 'disabled')", name="ck_sb_sites_status"),
        sa.UniqueConstraint("site_code", name="uq_sb_sites_code"),
    )

    op.create_table(
        "sb_surfaces",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_code", sa.String(length=80), nullable=False),
        sa.Column("surface_code", sa.String(length=40), nullable=False),
        sa.Column("surface_name", sa.String(length=120), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("status IN ('active', 'disabled')", name="ck_sb_surfaces_status"),
        sa.UniqueConstraint("site_code", "surface_code", name="uq_sb_surfaces_site_surface"),
    )

    op.create_table(
        "sb_pages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_code", sa.String(length=80), nullable=False),
        sa.Column("surface_code", sa.String(length=40), nullable=False),
        sa.Column("page_code", sa.String(length=80), nullable=False),
        sa.Column("page_title", sa.String(length=120), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'draft'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'published', 'disabled')",
            name="ck_sb_pages_status",
        ),
        sa.UniqueConstraint(
            "site_code",
            "surface_code",
            "page_code",
            name="uq_sb_pages_key",
        ),
    )

    op.create_table(
        "sb_regions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_code", sa.String(length=80), nullable=False),
        sa.Column("surface_code", sa.String(length=40), nullable=False),
        sa.Column("page_code", sa.String(length=80), nullable=False),
        sa.Column("region_code", sa.String(length=120), nullable=False),
        sa.Column("region_name", sa.String(length=120), nullable=False),
        sa.Column("region_type", sa.String(length=60), nullable=False),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("100"),
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("status IN ('active', 'disabled')", name="ck_sb_regions_status"),
        sa.UniqueConstraint(
            "site_code",
            "surface_code",
            "page_code",
            "region_code",
            name="uq_sb_regions_key",
        ),
    )
    op.create_index(
        "ix_sb_regions_page_sort",
        "sb_regions",
        ["site_code", "surface_code", "page_code", "sort_order", "region_code"],
    )

    op.create_table(
        "sb_blocks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_code", sa.String(length=80), nullable=False),
        sa.Column("surface_code", sa.String(length=40), nullable=False),
        sa.Column("page_code", sa.String(length=80), nullable=False),
        sa.Column("region_code", sa.String(length=120), nullable=False),
        sa.Column("block_code", sa.String(length=160), nullable=False),
        sa.Column("block_name", sa.String(length=120), nullable=False),
        sa.Column("block_type", sa.String(length=60), nullable=False),
        sa.Column("renderer_key", sa.String(length=120), nullable=False),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("100"),
        ),
        sa.Column(
            "content_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
        sa.Column(
            "layout_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("status IN ('active', 'disabled')", name="ck_sb_blocks_status"),
        sa.UniqueConstraint(
            "site_code",
            "surface_code",
            "page_code",
            "block_code",
            name="uq_sb_blocks_key",
        ),
    )
    op.create_index(
        "ix_sb_blocks_region_sort",
        "sb_blocks",
        ["site_code", "surface_code", "page_code", "region_code", "sort_order", "block_code"],
    )

    sites = sa.table(
        "sb_sites",
        sa.column("site_code", sa.String),
        sa.column("site_name", sa.String),
        sa.column("status", sa.String),
    )
    surfaces = sa.table(
        "sb_surfaces",
        sa.column("site_code", sa.String),
        sa.column("surface_code", sa.String),
        sa.column("surface_name", sa.String),
        sa.column("status", sa.String),
    )
    pages = sa.table(
        "sb_pages",
        sa.column("site_code", sa.String),
        sa.column("surface_code", sa.String),
        sa.column("page_code", sa.String),
        sa.column("page_title", sa.String),
        sa.column("status", sa.String),
    )

    op.bulk_insert(
        sites,
        [
            {
                "site_code": "default",
                "site_name": "默认站点",
                "status": "active",
            }
        ],
    )
    op.bulk_insert(
        surfaces,
        [
            {
                "site_code": "default",
                "surface_code": "pc_web",
                "surface_name": "PC Web",
                "status": "active",
            }
        ],
    )
    op.bulk_insert(
        pages,
        [
            {
                "site_code": "default",
                "surface_code": "pc_web",
                "page_code": "home",
                "page_title": "首页",
                "status": "draft",
            }
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_sb_blocks_region_sort", table_name="sb_blocks")
    op.drop_table("sb_blocks")
    op.drop_index("ix_sb_regions_page_sort", table_name="sb_regions")
    op.drop_table("sb_regions")
    op.drop_table("sb_pages")
    op.drop_table("sb_surfaces")
    op.drop_table("sb_sites")
