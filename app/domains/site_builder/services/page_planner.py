from sqlalchemy.orm import Session

from app.domains.site_builder.contracts.page_planner import PagePlannerOptionsResponse
from app.domains.site_builder.services.page_authoring_capabilities import (
    list_block_options,
    list_region_block_rules,
    list_region_options,
    list_template_region_options,
)
from app.domains.site_builder.services.page_authoring_context import require_page_context


def get_page_planner_options(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> PagePlannerOptionsResponse:
    context = require_page_context(session, site_code, surface_code, page_code)

    return PagePlannerOptionsResponse(
        template_key=context.template_key,
        template_name=context.template_name,
        template_regions=list_template_region_options(
            context.template_key,
            context.surface_code,
        ),
        allowed_region_types=list_region_options(context.template_key),
        allowed_block_types=list_block_options(),
        region_block_rules=list_region_block_rules(context.template_key),
    )
