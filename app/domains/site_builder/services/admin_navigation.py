from collections import defaultdict
from typing import Literal, Protocol, cast

from app.domains.site_builder.contracts.admin_pages import (
    SiteBuilderAdminPageDto,
    SiteBuilderNavigationResponse,
)

AdminPageStatus = Literal["connected", "planned", "disabled"]


class AdminPageLike(Protocol):
    page_code: str
    title: str
    parent_code: str | None
    level: int
    route_path: str
    component_key: str
    show_in_sidebar: bool
    sort_order: int
    status: str
    is_active: bool


def _normalize_status(value: str) -> AdminPageStatus:
    if value in {"connected", "planned", "disabled"}:
        return cast(AdminPageStatus, value)

    return "planned"


def _to_dto(
    page: AdminPageLike,
    children: list[SiteBuilderAdminPageDto],
) -> SiteBuilderAdminPageDto:
    return SiteBuilderAdminPageDto(
        page_code=page.page_code,
        title=page.title,
        parent_code=page.parent_code,
        level=page.level,
        route_path=page.route_path,
        component_key=page.component_key,
        show_in_sidebar=page.show_in_sidebar,
        sort_order=page.sort_order,
        status=_normalize_status(page.status),
        is_active=page.is_active,
        children=children,
    )


def build_admin_page_tree(
    pages: list[AdminPageLike],
) -> list[SiteBuilderAdminPageDto]:
    pages_by_code = {page.page_code: page for page in pages}
    children_by_parent: dict[str | None, list[AdminPageLike]] = defaultdict(list)

    for page in pages:
        if page.parent_code and page.parent_code not in pages_by_code:
            children_by_parent[None].append(page)
        else:
            children_by_parent[page.parent_code].append(page)

    for children in children_by_parent.values():
        children.sort(key=lambda item: (item.sort_order, item.page_code))

    def build(parent_code: str | None) -> list[SiteBuilderAdminPageDto]:
        return [_to_dto(page, build(page.page_code)) for page in children_by_parent[parent_code]]

    return build(None)


def build_navigation_response(
    pages: list[AdminPageLike],
) -> SiteBuilderNavigationResponse:
    return SiteBuilderNavigationResponse(
        app_code="d2c-site-builder",
        pages=build_admin_page_tree(pages),
    )
