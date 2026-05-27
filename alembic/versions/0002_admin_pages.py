"""add site builder admin pages

Revision ID: 0002_admin_pages
Revises: 0001_sb_base
Create Date: 2026-05-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_admin_pages"
down_revision: str | None = "0001_sb_base"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sb_admin_pages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("page_code", sa.String(length=160), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("parent_code", sa.String(length=160), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("route_path", sa.String(length=240), nullable=False),
        sa.Column("component_key", sa.String(length=180), nullable=False),
        sa.Column(
            "show_in_sidebar",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
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
            server_default=sa.text("'planned'"),
        ),
        sa.Column(
            "is_active",
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
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("level >= 1", name="ck_sb_admin_pages_level"),
        sa.CheckConstraint(
            "status IN ('connected', 'planned', 'disabled')",
            name="ck_sb_admin_pages_status",
        ),
        sa.UniqueConstraint("page_code", name="uq_sb_admin_pages_code"),
        sa.UniqueConstraint("route_path", name="uq_sb_admin_pages_route"),
    )
    op.create_index(
        "ix_sb_admin_pages_parent_sort",
        "sb_admin_pages",
        ["parent_code", "sort_order", "page_code"],
    )

    pages_table = sa.table(
        "sb_admin_pages",
        sa.column("page_code", sa.String),
        sa.column("title", sa.String),
        sa.column("parent_code", sa.String),
        sa.column("level", sa.Integer),
        sa.column("route_path", sa.String),
        sa.column("component_key", sa.String),
        sa.column("show_in_sidebar", sa.Boolean),
        sa.column("sort_order", sa.Integer),
        sa.column("status", sa.String),
        sa.column("is_active", sa.Boolean),
    )

    op.bulk_insert(
        pages_table,
        [
            {
                "page_code": "site_builder.dashboard",
                "title": "建站首页",
                "parent_code": None,
                "level": 1,
                "route_path": "/",
                "component_key": "site_builder.dashboard",
                "show_in_sidebar": True,
                "sort_order": 10,
                "status": "connected",
                "is_active": True,
            },
            {
                "page_code": "site_builder.pc_web",
                "title": "PC Web",
                "parent_code": None,
                "level": 1,
                "route_path": "/pc-web",
                "component_key": "layout.group",
                "show_in_sidebar": True,
                "sort_order": 20,
                "status": "connected",
                "is_active": True,
            },
            {
                "page_code": "site_builder.pc_web.overview",
                "title": "PC Web 总览",
                "parent_code": "site_builder.pc_web",
                "level": 2,
                "route_path": "/pc-web/overview",
                "component_key": "site_builder.pc_web.overview",
                "show_in_sidebar": True,
                "sort_order": 10,
                "status": "connected",
                "is_active": True,
            },
            {
                "page_code": "site_builder.pc_web.home",
                "title": "首页搭建",
                "parent_code": "site_builder.pc_web",
                "level": 2,
                "route_path": "/pc-web/home",
                "component_key": "site_builder.pc_web.home",
                "show_in_sidebar": True,
                "sort_order": 20,
                "status": "connected",
                "is_active": True,
            },
            {
                "page_code": "site_builder.pc_web.layout",
                "title": "全局框架",
                "parent_code": "site_builder.pc_web",
                "level": 2,
                "route_path": "/pc-web/layout",
                "component_key": "site_builder.pc_web.layout",
                "show_in_sidebar": True,
                "sort_order": 30,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.pc_web.category_landing",
                "title": "分类入口页",
                "parent_code": "site_builder.pc_web",
                "level": 2,
                "route_path": "/pc-web/category-landing",
                "component_key": "site_builder.pc_web.category_landing",
                "show_in_sidebar": True,
                "sort_order": 40,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.pc_web.product_list",
                "title": "商品列表页模板",
                "parent_code": "site_builder.pc_web",
                "level": 2,
                "route_path": "/pc-web/product-list",
                "component_key": "site_builder.pc_web.product_list",
                "show_in_sidebar": True,
                "sort_order": 50,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.pc_web.product_detail",
                "title": "商品详情页模板",
                "parent_code": "site_builder.pc_web",
                "level": 2,
                "route_path": "/pc-web/product-detail",
                "component_key": "site_builder.pc_web.product_detail",
                "show_in_sidebar": True,
                "sort_order": 60,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.pc_web.campaigns",
                "title": "活动页",
                "parent_code": "site_builder.pc_web",
                "level": 2,
                "route_path": "/pc-web/campaigns",
                "component_key": "site_builder.pc_web.campaigns",
                "show_in_sidebar": True,
                "sort_order": 70,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.pc_web.content_pages",
                "title": "内容页",
                "parent_code": "site_builder.pc_web",
                "level": 2,
                "route_path": "/pc-web/content-pages",
                "component_key": "site_builder.pc_web.content_pages",
                "show_in_sidebar": True,
                "sort_order": 80,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.publish",
                "title": "发布中心",
                "parent_code": None,
                "level": 1,
                "route_path": "/publish",
                "component_key": "layout.group",
                "show_in_sidebar": True,
                "sort_order": 30,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.publish.check",
                "title": "发布检查",
                "parent_code": "site_builder.publish",
                "level": 2,
                "route_path": "/publish/check",
                "component_key": "site_builder.publish.check",
                "show_in_sidebar": True,
                "sort_order": 10,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.publish.runtime",
                "title": "Runtime Contract",
                "parent_code": "site_builder.publish",
                "level": 2,
                "route_path": "/publish/runtime",
                "component_key": "site_builder.publish.runtime",
                "show_in_sidebar": True,
                "sort_order": 20,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.settings",
                "title": "系统设置",
                "parent_code": None,
                "level": 1,
                "route_path": "/settings",
                "component_key": "layout.group",
                "show_in_sidebar": True,
                "sort_order": 40,
                "status": "planned",
                "is_active": True,
            },
            {
                "page_code": "site_builder.settings.site",
                "title": "站点设置",
                "parent_code": "site_builder.settings",
                "level": 2,
                "route_path": "/settings/site",
                "component_key": "site_builder.settings.site",
                "show_in_sidebar": True,
                "sort_order": 10,
                "status": "planned",
                "is_active": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_sb_admin_pages_parent_sort", table_name="sb_admin_pages")
    op.drop_table("sb_admin_pages")
