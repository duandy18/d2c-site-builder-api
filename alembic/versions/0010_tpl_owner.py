"""add template owner tables

Revision ID: 0010_tpl_owner
Revises: 0009_pub_preview
Create Date: 2026-05-28
"""

# ruff: noqa: E501, UP031
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0010_tpl_owner"
down_revision: str | Sequence[str] | None = "0009_pub_preview"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create template owner tables and migrate PC Web templates to DB."""

    op.create_table(
        "sb_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("template_key", sa.String(length=120), nullable=False),
        sa.Column("template_name", sa.String(length=160), nullable=False),
        sa.Column("surface_code", sa.String(length=40), nullable=False),
        sa.Column("page_code", sa.String(length=80), nullable=False),
        sa.Column("template_version", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("100")),
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
        sa.CheckConstraint("status IN ('active', 'disabled')", name="ck_sb_templates_status"),
        sa.UniqueConstraint("template_key", name="uq_sb_templates_key"),
        sa.UniqueConstraint("surface_code", "page_code", name="uq_sb_templates_surface_page"),
    )
    op.create_index(
        "ix_sb_templates_surface_sort",
        "sb_templates",
        ["surface_code", "sort_order", "template_key"],
    )

    op.create_table(
        "sb_template_regions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("template_key", sa.String(length=120), nullable=False),
        sa.Column("template_region_code", sa.String(length=80), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("default_region_name", sa.String(length=120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("100")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
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
        sa.ForeignKeyConstraint(
            ["template_key"], ["sb_templates.template_key"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "status IN ('active', 'disabled')", name="ck_sb_template_regions_status"
        ),
        sa.UniqueConstraint("template_key", "template_region_code", name="uq_sb_tpl_regions_key"),
    )
    op.create_index(
        "ix_sb_tpl_regions_sort",
        "sb_template_regions",
        ["template_key", "sort_order", "template_region_code"],
    )

    op.create_table(
        "sb_template_slots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("template_key", sa.String(length=120), nullable=False),
        sa.Column("template_region_code", sa.String(length=80), nullable=False),
        sa.Column("slot_code", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("block_type", sa.String(length=80), nullable=False),
        sa.Column("renderer_key", sa.String(length=120), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("default_block_name", sa.String(length=120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("100")),
        sa.Column(
            "content_schema_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")
        ),
        sa.Column(
            "presentation_schema_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
        sa.Column(
            "default_content_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")
        ),
        sa.Column(
            "default_presentation_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
        sa.Column(
            "validation_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")
        ),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
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
        sa.ForeignKeyConstraint(
            ["template_key"], ["sb_templates.template_key"], ondelete="CASCADE"
        ),
        sa.CheckConstraint("status IN ('active', 'disabled')", name="ck_sb_template_slots_status"),
        sa.UniqueConstraint("template_key", "slot_code", name="uq_sb_tpl_slots_key"),
    )
    op.create_index(
        "ix_sb_tpl_slots_region_sort",
        "sb_template_slots",
        ["template_key", "template_region_code", "sort_order", "slot_code"],
    )

    op.add_column("sb_pages", sa.Column("template_key", sa.String(length=120), nullable=True))
    op.add_column(
        "sb_blocks",
        sa.Column(
            "presentation_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
    )

    op.execute(
        """
        UPDATE sb_blocks
        SET presentation_json = layout_json
        WHERE layout_json IS NOT NULL
        """
    )

    _seed_templates()
    _retire_old_pc_web_pages()
    _register_new_pc_web_pages()

    op.alter_column("sb_pages", "template_key", nullable=False)
    op.create_foreign_key(
        "fk_sb_pages_template_key",
        "sb_pages",
        "sb_templates",
        ["template_key"],
        ["template_key"],
    )
    op.drop_column("sb_blocks", "layout_json")


def downgrade() -> None:
    """Return to legacy hard-coded template state."""

    op.add_column(
        "sb_blocks",
        sa.Column(
            "layout_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
    )
    op.execute(
        """
        UPDATE sb_blocks
        SET layout_json = presentation_json
        WHERE presentation_json IS NOT NULL
        """
    )
    op.drop_column("sb_blocks", "presentation_json")

    op.drop_constraint("fk_sb_pages_template_key", "sb_pages", type_="foreignkey")
    op.drop_column("sb_pages", "template_key")

    op.drop_table("sb_template_slots")
    op.drop_table("sb_template_regions")
    op.drop_table("sb_templates")


def _seed_templates() -> None:
    templates = (
        (
            "pc_home_simple_shop_v1",
            "极简商品型首页",
            "pc_web",
            "home",
            "v1",
            "首页承担商品浏览、分类筛选、活动曝光和加购物车入口。",
            10,
        ),
        (
            "pc_product_detail_gallery_v1",
            "标准图册商品详情页",
            "pc_web",
            "product_detail_gallery",
            "v1",
            "左侧主图和缩略图，右侧购买信息。",
            20,
        ),
        (
            "pc_product_detail_image_matrix_v1",
            "多图展示商品详情页",
            "pc_web",
            "product_detail_image_matrix",
            "v1",
            "图片权重更高，周围多角度图点击切换主图。",
            30,
        ),
    )

    values = ",\n".join("('%s','%s','%s','%s','%s','%s','active',%s)" % item for item in templates)
    op.execute(
        f"""
        INSERT INTO sb_templates (
          template_key,
          template_name,
          surface_code,
          page_code,
          template_version,
          description,
          status,
          sort_order
        )
        VALUES
          {values}
        """
    )

    _seed_home_template()
    _seed_product_detail_gallery_template()
    _seed_product_detail_image_matrix_template()


def _seed_home_template() -> None:
    _insert_regions(
        "pc_home_simple_shop_v1",
        (
            ("home.header", "顶部导航", "品牌和登录入口", True, "顶部导航", 10),
            (
                "home.product_collection",
                "商品集合导航",
                "全部、新品、热卖、推荐、大促",
                True,
                "商品集合导航",
                20,
            ),
            ("home.hero", "首页标题", "首页主标题", True, "首页标题", 30),
            ("home.campaign", "首页广告位", "首页标题下方广告位", True, "首页广告位", 40),
            (
                "home.product_category",
                "商品分类导航",
                "商品分类和小黄车入口",
                True,
                "商品分类导航",
                50,
            ),
            ("home.product_grid", "商品列表", "商品列表和商品卡", True, "商品列表", 60),
            ("home.service", "服务承诺", "包邮、发货、新客礼", False, "服务承诺", 70),
            ("home.legal_footer", "备案信息", "ICP 和公安备案占位", False, "备案信息", 80),
        ),
    )

    _insert_slots(
        "pc_home_simple_shop_v1",
        (
            (
                "home.header",
                "header.brand",
                "品牌名称",
                "品牌名称",
                "shop_header_brand",
                "pc_web.shop_header_brand",
                True,
                10,
                _schema("brand_name"),
            ),
            (
                "home.header",
                "header.login_link",
                "登录入口",
                "登录入口",
                "login_link",
                "pc_web.login_link",
                True,
                20,
                _schema("label", "link_target"),
            ),
            (
                "home.product_collection",
                "product_collection.tabs",
                "商品集合导航",
                "商品集合导航",
                "product_collection_tabs",
                "pc_web.product_collection_tabs",
                True,
                10,
                _schema("items"),
            ),
            (
                "home.hero",
                "hero.title",
                "首页标题",
                "首页标题",
                "simple_title",
                "pc_web.simple_title",
                True,
                10,
                _schema("kicker", "title"),
            ),
            (
                "home.campaign",
                "campaign.banner",
                "首页广告位",
                "首页广告位",
                "campaign_banner",
                "pc_web.campaign_banner",
                True,
                10,
                _schema("title", optional_fields=("label", "subtitle", "link_target")),
            ),
            (
                "home.product_category",
                "product_category.nav",
                "商品分类导航",
                "商品分类导航",
                "product_category_nav",
                "pc_web.product_category_nav",
                True,
                10,
                _schema("items"),
            ),
            (
                "home.product_category",
                "cart.entry",
                "购物车入口",
                "购物车入口",
                "cart_icon_link",
                "pc_web.cart_icon_link",
                True,
                20,
                _schema("link_target"),
            ),
            (
                "home.product_grid",
                "product_grid.list",
                "商品列表",
                "商品列表",
                "product_grid",
                "pc_web.product_grid",
                True,
                10,
                _schema("source", "products"),
            ),
            (
                "home.service",
                "service.promise_bar",
                "服务承诺",
                "服务承诺",
                "service_promise_bar",
                "pc_web.service_promise_bar",
                False,
                10,
                _schema("items"),
            ),
            (
                "home.legal_footer",
                "site.legal_footer",
                "网站备案信息",
                "网站备案信息",
                "legal_footer",
                "pc_web.legal_footer",
                False,
                10,
                _schema("copyright_text", "icp_record_number", "police_record_number"),
            ),
        ),
    )


def _seed_product_detail_gallery_template() -> None:
    _insert_regions(
        "pc_product_detail_gallery_v1",
        (
            ("product.gallery", "商品图册", "主图和缩略图", True, "商品图册", 10),
            (
                "product.summary",
                "商品购买信息",
                "商品标题、价格、优惠和购买动作",
                True,
                "商品购买信息",
                20,
            ),
            ("product.detail_content", "商品详情说明", "商品说明卡片", False, "商品详情说明", 30),
            ("product.recommend", "相关推荐", "推荐商品货架", False, "相关推荐", 40),
        ),
    )

    _insert_slots(
        "pc_product_detail_gallery_v1",
        (
            (
                "product.gallery",
                "product.gallery.main",
                "商品主图",
                "商品主图",
                "product_gallery_main",
                "pc_web.product_gallery_main",
                True,
                10,
                _schema("main_image"),
            ),
            (
                "product.gallery",
                "product.gallery.thumbs",
                "商品缩略图",
                "商品缩略图",
                "product_gallery_thumbs",
                "pc_web.product_gallery_thumbs",
                True,
                20,
                _schema("images"),
            ),
            (
                "product.summary",
                "product.summary.info",
                "商品基本信息",
                "商品基本信息",
                "product_summary_info",
                "pc_web.product_summary_info",
                True,
                10,
                _schema("category", "title", "description"),
            ),
            (
                "product.summary",
                "product.price",
                "商品价格",
                "商品价格",
                "product_price",
                "pc_web.product_price",
                True,
                20,
                _schema("sale_price", "original_price"),
            ),
            (
                "product.summary",
                "product.promotion",
                "商品优惠",
                "商品优惠",
                "product_promotion",
                "pc_web.product_promotion",
                False,
                30,
                _schema("badge", "promo"),
            ),
            (
                "product.summary",
                "product.sales_stats",
                "销售数据",
                "销售数据",
                "product_sales_stats",
                "pc_web.product_sales_stats",
                False,
                40,
                _schema("sold_count", "paid_buyers"),
            ),
            (
                "product.summary",
                "product.highlights",
                "商品卖点",
                "商品卖点",
                "product_highlight_list",
                "pc_web.product_highlight_list",
                False,
                50,
                _schema("items"),
            ),
            (
                "product.summary",
                "product.quantity",
                "数量选择",
                "数量选择",
                "quantity_select",
                "pc_web.quantity_select",
                True,
                60,
                _schema(),
            ),
            (
                "product.summary",
                "product.cart_action",
                "加入购物车",
                "加入购物车",
                "add_to_cart_button",
                "pc_web.add_to_cart_button",
                True,
                70,
                _schema("label"),
            ),
            (
                "product.detail_content",
                "product.detail_content.cards",
                "商品详情说明卡",
                "商品详情说明卡",
                "product_detail_cards",
                "pc_web.product_detail_cards",
                False,
                10,
                _schema("cards"),
            ),
            (
                "product.recommend",
                "product.recommend_shelf",
                "相关推荐",
                "相关推荐",
                "product_recommend_shelf",
                "pc_web.product_recommend_shelf",
                False,
                10,
                _schema("source"),
            ),
        ),
    )


def _seed_product_detail_image_matrix_template() -> None:
    _insert_regions(
        "pc_product_detail_image_matrix_v1",
        (
            ("product.image_matrix", "多图展示", "主图和多角度图片", True, "多图展示", 10),
            (
                "product.summary",
                "商品购买信息",
                "商品标题、价格、优惠和购买动作",
                True,
                "商品购买信息",
                20,
            ),
            ("product.detail_content", "图文说明", "图文说明卡片", False, "图文说明", 30),
        ),
    )

    _insert_slots(
        "pc_product_detail_image_matrix_v1",
        (
            (
                "product.image_matrix",
                "product.image_matrix.main",
                "多图主图",
                "多图主图",
                "product_image_matrix_main",
                "pc_web.product_image_matrix_main",
                True,
                10,
                _schema("main_image"),
            ),
            (
                "product.image_matrix",
                "product.image_matrix.side_images",
                "多角度图片",
                "多角度图片",
                "product_image_matrix_side_images",
                "pc_web.product_image_matrix_side_images",
                True,
                20,
                _schema("images"),
            ),
            (
                "product.summary",
                "product.summary.info",
                "商品基本信息",
                "商品基本信息",
                "product_summary_info",
                "pc_web.product_summary_info",
                True,
                10,
                _schema("category", "title", "description"),
            ),
            (
                "product.summary",
                "product.price",
                "商品价格",
                "商品价格",
                "product_price",
                "pc_web.product_price",
                True,
                20,
                _schema("sale_price", "original_price"),
            ),
            (
                "product.summary",
                "product.promotion",
                "商品优惠",
                "商品优惠",
                "product_promotion",
                "pc_web.product_promotion",
                False,
                30,
                _schema("promo"),
            ),
            (
                "product.summary",
                "product.sales_stats",
                "销售数据",
                "销售数据",
                "product_sales_stats",
                "pc_web.product_sales_stats",
                False,
                40,
                _schema("sold_count", "paid_buyers"),
            ),
            (
                "product.summary",
                "product.highlights",
                "商品卖点",
                "商品卖点",
                "product_highlight_list",
                "pc_web.product_highlight_list",
                False,
                50,
                _schema("items"),
            ),
            (
                "product.summary",
                "product.quantity",
                "数量选择",
                "数量选择",
                "quantity_select",
                "pc_web.quantity_select",
                True,
                60,
                _schema(),
            ),
            (
                "product.summary",
                "product.cart_action",
                "加入购物车",
                "加入购物车",
                "add_to_cart_button",
                "pc_web.add_to_cart_button",
                True,
                70,
                _schema("label"),
            ),
            (
                "product.detail_content",
                "product.detail_content.cards",
                "图文说明",
                "图文说明",
                "product_detail_cards",
                "pc_web.product_detail_cards",
                False,
                10,
                _schema("cards"),
            ),
        ),
    )


def _insert_regions(
    template_key: str, rows: tuple[tuple[str, str, str, bool, str, int], ...]
) -> None:
    values = ",\n".join(
        "('%s','%s','%s','%s',%s,'%s',%s,'active')"
        % (
            template_key,
            code,
            label,
            description,
            "TRUE" if required else "FALSE",
            default_name,
            sort_order,
        )
        for code, label, description, required, default_name, sort_order in rows
    )
    op.execute(
        f"""
        INSERT INTO sb_template_regions (
          template_key,
          template_region_code,
          label,
          description,
          required,
          default_region_name,
          sort_order,
          status
        )
        VALUES
          {values}
        """
    )


def _insert_slots(
    template_key: str, rows: tuple[tuple[str, str, str, str, str, str, bool, int, str], ...]
) -> None:
    values = ",\n".join(
        "('%s','%s','%s','%s','%s','%s','%s',%s,'%s',%s,%s::json,'{}'::json,'{}'::json,'{}'::json,'{}'::json,'active')"
        % (
            template_key,
            region_code,
            slot_code,
            label,
            description,
            block_type,
            renderer_key,
            "TRUE" if required else "FALSE",
            label,
            sort_order,
            content_schema,
        )
        for region_code, slot_code, label, description, block_type, renderer_key, required, sort_order, content_schema in rows
    )
    op.execute(
        f"""
        INSERT INTO sb_template_slots (
          template_key,
          template_region_code,
          slot_code,
          label,
          description,
          block_type,
          renderer_key,
          required,
          default_block_name,
          sort_order,
          content_schema_json,
          presentation_schema_json,
          default_content_json,
          default_presentation_json,
          validation_json,
          status
        )
        VALUES
          {values}
        """
    )


def _schema(
    *required_fields: str,
    optional_fields: tuple[str, ...] = (),
) -> str:
    import json

    fields = {field: {"required": True} for field in required_fields}
    fields.update({field: {"required": False} for field in optional_fields})

    schema = {"fields": fields}
    encoded = json.dumps(schema, ensure_ascii=False).replace("'", "''")

    return f"'{encoded}'"


def _retire_old_pc_web_pages() -> None:
    old_pages = "'category_entry','product_list','campaign','content_page'"
    op.execute(
        f"DELETE FROM sb_blocks WHERE site_code='default' AND surface_code='pc_web' AND page_code IN ({old_pages})"
    )
    op.execute(
        f"DELETE FROM sb_regions WHERE site_code='default' AND surface_code='pc_web' AND page_code IN ({old_pages})"
    )
    op.execute(
        f"DELETE FROM sb_pages WHERE site_code='default' AND surface_code='pc_web' AND page_code IN ({old_pages})"
    )
    op.execute(
        """
        DELETE FROM sb_admin_pages
        WHERE page_code IN (
          'site_builder.pc_web.category_entry',
          'site_builder.pc_web.product_list',
          'site_builder.pc_web.campaign',
          'site_builder.pc_web.content_page'
        )
        """
    )


def _register_new_pc_web_pages() -> None:
    op.execute(
        """
        DELETE FROM sb_blocks
        WHERE site_code='default'
          AND surface_code='pc_web'
          AND page_code='home'
        """
    )
    op.execute(
        """
        DELETE FROM sb_regions
        WHERE site_code='default'
          AND surface_code='pc_web'
          AND page_code='home'
        """
    )
    op.execute(
        """
        UPDATE sb_pages
        SET
          template_key='pc_home_simple_shop_v1',
          page_title='首页'
        WHERE site_code='default'
          AND surface_code='pc_web'
          AND page_code='home'
        """
    )
    op.execute(
        """
        INSERT INTO sb_pages (
          site_code,
          surface_code,
          page_code,
          page_title,
          template_key,
          status
        )
        VALUES
          ('default','pc_web','product_detail_gallery','商品详情页A','pc_product_detail_gallery_v1','draft'),
          ('default','pc_web','product_detail_image_matrix','商品详情页B','pc_product_detail_image_matrix_v1','draft')
        ON CONFLICT (site_code, surface_code, page_code) DO UPDATE
        SET
          page_title=EXCLUDED.page_title,
          template_key=EXCLUDED.template_key,
          status=EXCLUDED.status,
          updated_at=now()
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
            'site_builder.pc_web.product_detail_gallery',
            '商品详情页A',
            'site_builder.pc_web',
            2,
            '/pc-web/product-detail-gallery',
            'site_builder.pc_web.template_content',
            TRUE,
            40,
            'connected',
            TRUE
          ),
          (
            'site_builder.pc_web.product_detail_image_matrix',
            '商品详情页B',
            'site_builder.pc_web',
            2,
            '/pc-web/product-detail-image-matrix',
            'site_builder.pc_web.template_content',
            TRUE,
            50,
            'connected',
            TRUE
          )
        ON CONFLICT (page_code) DO UPDATE
        SET
          title=EXCLUDED.title,
          parent_code=EXCLUDED.parent_code,
          level=EXCLUDED.level,
          route_path=EXCLUDED.route_path,
          component_key=EXCLUDED.component_key,
          show_in_sidebar=EXCLUDED.show_in_sidebar,
          sort_order=EXCLUDED.sort_order,
          status=EXCLUDED.status,
          is_active=EXCLUDED.is_active,
          updated_at=now()
        """
    )
