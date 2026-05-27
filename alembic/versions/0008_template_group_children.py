"""promote template catalog to grouped children

Revision ID: 0008_template_group_children
Revises: 0007_template_catalog_root
Create Date: 2026-05-28 01:05:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0008_template_group_children"
down_revision: str | Sequence[str] | None = "0007_template_catalog_root"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Replace root template leaf with template group and surface child pages."""

    op.execute(
        """
        DELETE FROM sb_admin_pages
        WHERE page_code IN (
          'site_builder.dashboard',
          'site_builder.pc_web.templates',
          'site_builder.templates',
          'site_builder.templates.pc_web',
          'site_builder.templates.mobile_web',
          'site_builder.templates.mini_program'
        )
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
        VALUES
          (
            'site_builder.templates',
            '建站模板',
            NULL,
            1,
            '/',
            'layout.group',
            TRUE,
            10,
            'connected',
            TRUE
          ),
          (
            'site_builder.templates.pc_web',
            'PC Web 模板',
            'site_builder.templates',
            2,
            '/templates/pc-web',
            'site_builder.template_catalog',
            TRUE,
            10,
            'connected',
            TRUE
          ),
          (
            'site_builder.templates.mobile_web',
            '手机 Web 模板',
            'site_builder.templates',
            2,
            '/templates/mobile-web',
            'site_builder.template_catalog',
            TRUE,
            20,
            'planned',
            TRUE
          ),
          (
            'site_builder.templates.mini_program',
            '小程序模板',
            'site_builder.templates',
            2,
            '/templates/mini-program',
            'site_builder.template_catalog',
            TRUE,
            30,
            'planned',
            TRUE
          )
        """
    )


def downgrade() -> None:
    """Restore the 0007 root template catalog leaf."""

    op.execute(
        """
        DELETE FROM sb_admin_pages
        WHERE page_code IN (
          'site_builder.templates',
          'site_builder.templates.pc_web',
          'site_builder.templates.mobile_web',
          'site_builder.templates.mini_program'
        )
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
          'site_builder.dashboard',
          '建站模板',
          NULL,
          1,
          '/',
          'site_builder.template_catalog',
          TRUE,
          10,
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
