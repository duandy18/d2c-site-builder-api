"""add pc web template pages

Revision ID: 0004_pc_web_template_pages
Revises: 0003_pc_home
Create Date: 2026-05-27 22:30:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0004_pc_web_template_pages"
down_revision: str | Sequence[str] | None = "0003_pc_home"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


PAGE_ROWS = (
    ("default", "pc_web", "category_entry", "分类入口页"),
    ("default", "pc_web", "product_list", "商品列表页"),
    ("default", "pc_web", "campaign", "活动页"),
    ("default", "pc_web", "content_page", "内容页"),
)


def upgrade() -> None:
    """Register PC Web template-driven pages."""

    values = ",\n".join(
        f"('{site_code}', '{surface_code}', '{page_code}', '{page_title}')"
        for site_code, surface_code, page_code, page_title in PAGE_ROWS
    )

    op.execute(
        f"""
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'sb_pages'
              AND column_name = 'status'
          ) THEN
            INSERT INTO sb_pages (
              site_code,
              surface_code,
              page_code,
              page_title,
              status
            )
            SELECT site_code, surface_code, page_code, page_title, 'draft'
            FROM (
              VALUES
                {values}
            ) AS v(site_code, surface_code, page_code, page_title)
            ON CONFLICT DO NOTHING;
          ELSE
            INSERT INTO sb_pages (
              site_code,
              surface_code,
              page_code,
              page_title
            )
            SELECT site_code, surface_code, page_code, page_title
            FROM (
              VALUES
                {values}
            ) AS v(site_code, surface_code, page_code, page_title)
            ON CONFLICT DO NOTHING;
          END IF;
        END $$;
        """
    )


def downgrade() -> None:
    """Remove registered PC Web template-driven pages."""

    op.execute(
        """
        DELETE FROM sb_blocks
        WHERE site_code = 'default'
          AND surface_code = 'pc_web'
          AND page_code IN (
            'category_entry',
            'product_list',
            'campaign',
            'content_page'
          )
        """
    )

    op.execute(
        """
        DELETE FROM sb_regions
        WHERE site_code = 'default'
          AND surface_code = 'pc_web'
          AND page_code IN (
            'category_entry',
            'product_list',
            'campaign',
            'content_page'
          )
        """
    )

    op.execute(
        """
        DELETE FROM sb_pages
        WHERE site_code = 'default'
          AND surface_code = 'pc_web'
          AND page_code IN (
            'category_entry',
            'product_list',
            'campaign',
            'content_page'
          )
        """
    )
