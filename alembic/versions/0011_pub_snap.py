"""add published page snapshots

Revision ID: 0011_pub_snap
Revises: 0010_tpl_owner
Create Date: 2026-05-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0011_pub_snap"
down_revision: str | Sequence[str] | None = "0010_tpl_owner"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sb_published_page_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_code", sa.String(length=80), nullable=False),
        sa.Column("surface_code", sa.String(length=40), nullable=False),
        sa.Column("page_code", sa.String(length=80), nullable=False),
        sa.Column("publish_version", sa.Integer(), nullable=False),
        sa.Column("template_key", sa.String(length=120), nullable=False),
        sa.Column("template_version", sa.String(length=32), nullable=False),
        sa.Column("contract_version", sa.String(length=40), nullable=False),
        sa.Column("snapshot_json", sa.JSON(), nullable=False),
        sa.Column("readiness_json", sa.JSON(), nullable=False),
        sa.Column(
            "published_by",
            sa.String(length=120),
            nullable=False,
            server_default="system",
        ),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "is_current",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "site_code",
            "surface_code",
            "page_code",
            "publish_version",
            name="uq_sb_pub_snap_ver",
        ),
    )
    op.create_index(
        "ix_sb_pub_snap_current",
        "sb_published_page_snapshots",
        ["site_code", "surface_code", "page_code", "is_current"],
    )
    op.create_index(
        "ix_sb_pub_snap_page",
        "sb_published_page_snapshots",
        ["site_code", "surface_code", "page_code", "published_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_sb_pub_snap_page", table_name="sb_published_page_snapshots")
    op.drop_index("ix_sb_pub_snap_current", table_name="sb_published_page_snapshots")
    op.drop_table("sb_published_page_snapshots")
