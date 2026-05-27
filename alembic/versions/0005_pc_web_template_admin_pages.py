"""add pc web template admin pages

Revision ID: 0005_pc_web_template_admin_pages
Revises: 0004_pc_web_template_pages
Create Date: 2026-05-27 22:55:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0005_pc_web_template_admin_pages"
down_revision: str | Sequence[str] | None = "0004_pc_web_template_pages"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Promote existing planned PC Web template pages to connected routes."""

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          page_code = 'site_builder.pc_web.category_entry',
          title = '分类入口页',
          route_path = '/pc-web/category-entry',
          component_key = 'site_builder.pc_web.template_content',
          sort_order = 40,
          status = 'connected',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.pc_web.category_landing'
        """
    )

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          title = '商品列表页',
          route_path = '/pc-web/product-list',
          component_key = 'site_builder.pc_web.template_content',
          sort_order = 50,
          status = 'connected',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.pc_web.product_list'
        """
    )

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          page_code = 'site_builder.pc_web.campaign',
          title = '活动页',
          route_path = '/pc-web/campaign',
          component_key = 'site_builder.pc_web.template_content',
          sort_order = 70,
          status = 'connected',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.pc_web.campaigns'
        """
    )

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          page_code = 'site_builder.pc_web.content_page',
          title = '内容页',
          route_path = '/pc-web/content-page',
          component_key = 'site_builder.pc_web.template_content',
          sort_order = 80,
          status = 'connected',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.pc_web.content_pages'
        """
    )


def downgrade() -> None:
    """Restore PC Web template pages to their original planned registrations."""

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          page_code = 'site_builder.pc_web.category_landing',
          title = '分类入口页',
          route_path = '/pc-web/category-landing',
          component_key = 'site_builder.pc_web.category_landing',
          sort_order = 40,
          status = 'planned',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.pc_web.category_entry'
        """
    )

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          title = '商品列表页模板',
          route_path = '/pc-web/product-list',
          component_key = 'site_builder.pc_web.product_list',
          sort_order = 50,
          status = 'planned',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.pc_web.product_list'
        """
    )

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          page_code = 'site_builder.pc_web.campaigns',
          title = '活动页',
          route_path = '/pc-web/campaigns',
          component_key = 'site_builder.pc_web.campaigns',
          sort_order = 70,
          status = 'planned',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.pc_web.campaign'
        """
    )

    op.execute(
        """
        UPDATE sb_admin_pages
        SET
          page_code = 'site_builder.pc_web.content_pages',
          title = '内容页',
          route_path = '/pc-web/content-pages',
          component_key = 'site_builder.pc_web.content_pages',
          sort_order = 80,
          status = 'planned',
          is_active = TRUE,
          updated_at = now()
        WHERE page_code = 'site_builder.pc_web.content_page'
        """
    )
