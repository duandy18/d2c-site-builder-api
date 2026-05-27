"""add pc web template catalog

Revision ID: 0006_pc_web_template_catalog
Revises: 0005_pc_web_template_admin_pages
Create Date: 2026-05-28 00:05:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0006_pc_web_template_catalog"
down_revision: str | Sequence[str] | None = "0005_pc_web_template_admin_pages"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Delete unused placeholder PC Web pages and register template catalog."""

    op.execute(
        """
        DELETE FROM sb_admin_pages
        WHERE page_code IN (
          'site_builder.pc_web.overview',
          'site_builder.pc_web.layout',
          'site_builder.pc_web.product_detail'
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


def downgrade() -> None:
    """Restore deleted placeholder PC Web pages and remove template catalog."""

    op.execute(
        """
        DELETE FROM sb_admin_pages
        WHERE page_code = 'site_builder.pc_web.templates'
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
            'site_builder.pc_web.overview',
            'PC Web 总览',
            'site_builder.pc_web',
            2,
            '/pc-web/overview',
            'site_builder.pc_web.overview',
            TRUE,
            10,
            'connected',
            TRUE
          ),
          (
            'site_builder.pc_web.layout',
            '全局框架',
            'site_builder.pc_web',
            2,
            '/pc-web/layout',
            'site_builder.pc_web.layout',
            TRUE,
            30,
            'planned',
            TRUE
          ),
          (
            'site_builder.pc_web.product_detail',
            '商品详情页模板',
            'site_builder.pc_web',
            2,
            '/pc-web/product-detail',
            'site_builder.pc_web.product_detail',
            TRUE,
            60,
            'planned',
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
