"""register publish preview page

Revision ID: 0009_pub_preview
Revises: 0008_template_group_children
Create Date: 2026-05-28 01:45:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0009_pub_preview"
down_revision: str | Sequence[str] | None = "0008_template_group_children"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Register publish preview page under publish center."""

    op.execute(
        """
        INSERT INTO sb_admin_pages (
          page_code,
          title,
          parent_code,
          level,
          route_path,
          component_key,
          show_in_sidebar,
          sort_order,
          status,
          is_active
        )
        VALUES (
          'site_builder.publish.preview',
          '页面预览',
          'site_builder.publish',
          2,
          '/publish/preview',
          'site_builder.publish.preview',
          TRUE,
          5,
          'connected',
          TRUE
        )
        ON CONFLICT (page_code) DO UPDATE
        SET
          title = EXCLUDED.title,
          parent_code = EXCLUDED.parent_code,
          level = EXCLUDED.level,
          route_path = EXCLUDED.route_path,
          component_key = EXCLUDED.component_key,
          show_in_sidebar = EXCLUDED.show_in_sidebar,
          sort_order = EXCLUDED.sort_order,
          status = EXCLUDED.status,
          is_active = EXCLUDED.is_active,
          updated_at = now()
        """
    )


def downgrade() -> None:
    """Remove publish preview page."""

    op.execute(
        """
        DELETE FROM sb_admin_pages
        WHERE page_code = 'site_builder.publish.preview'
        """
    )
