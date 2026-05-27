"""promote template catalog to root

Revision ID: 0007_template_catalog_root
Revises: 0006_pc_web_template_catalog
Create Date: 2026-05-28 00:30:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0007_template_catalog_root"
down_revision: str | Sequence[str] | None = "0006_pc_web_template_catalog"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Promote template catalog to root and delete duplicated PC Web entry."""

    op.execute(
        """
        DELETE FROM sb_admin_pages
        WHERE page_code = 'site_builder.pc_web.templates'
        """
    )

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          title = '建站模板',
          route_path = '/',
          component_key = 'site_builder.template_catalog',
          show_in_sidebar = TRUE,
          sort_order = 10,
          status = 'connected',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.dashboard'
        """
    )


def downgrade() -> None:
    """Restore root dashboard and duplicated PC Web template catalog entry."""

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          title = '建站首页',
          route_path = '/',
          component_key = 'site_builder.dashboard',
          show_in_sidebar = TRUE,
          sort_order = 10,
          status = 'connected',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.dashboard'
        """
    )

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
          'site_builder.pc_web.templates',
          '模板中心',
          'site_builder.pc_web',
          2,
          '/pc-web/templates',
          'site_builder.pc_web.template_catalog',
          TRUE,
          30,
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
