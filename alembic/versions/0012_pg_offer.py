"""require offer code in product grid products

Revision ID: 0012_pg_offer
Revises: 0011_pub_snap
Create Date: 2026-05-28
"""

import json
from collections.abc import Sequence

from alembic import op

revision: str = "0012_pg_offer"
down_revision: str | Sequence[str] | None = "0011_pub_snap"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


PRODUCT_GRID_SCHEMA = {
    "fields": {
        "source": {"required": True},
        "products": {
            "required": True,
            "type": "array",
            "item_schema": {
                "fields": {
                    "offer_code": {"required": True},
                    "title": {"required": True},
                    "category": {"required": False},
                    "image": {"required": False},
                    "sale_price": {"required": False},
                    "original_price": {"required": False},
                    "sold_count": {"required": False},
                    "paid_buyers": {"required": False},
                }
            },
        },
    }
}

LEGACY_PRODUCT_GRID_SCHEMA = {
    "fields": {
        "source": {"required": True},
        "products": {"required": True},
    }
}


def upgrade() -> None:
    schema_json = _sql_json(PRODUCT_GRID_SCHEMA)
    validation_json = _sql_json({"products_require_offer_code": True})

    op.execute(
        f"""
        UPDATE sb_template_slots
        SET
          content_schema_json = '{schema_json}'::json,
          validation_json = '{validation_json}'::json,
          updated_at = now()
        WHERE template_key = 'pc_home_simple_shop_v1'
          AND slot_code = 'product_grid.list'
        """
    )


def downgrade() -> None:
    schema_json = _sql_json(LEGACY_PRODUCT_GRID_SCHEMA)

    op.execute(
        f"""
        UPDATE sb_template_slots
        SET
          content_schema_json = '{schema_json}'::json,
          validation_json = '{{}}'::json,
          updated_at = now()
        WHERE template_key = 'pc_home_simple_shop_v1'
          AND slot_code = 'product_grid.list'
        """
    )


def _sql_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False).replace("'", "''")
