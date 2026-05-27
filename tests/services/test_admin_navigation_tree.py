from types import SimpleNamespace

from app.domains.site_builder.services.admin_navigation import build_navigation_response


def test_build_navigation_response_groups_children_by_parent() -> None:
    pages = [
        SimpleNamespace(
            page_code="site_builder.pc_web.home",
            title="首页搭建",
            parent_code="site_builder.pc_web",
            level=2,
            route_path="/pc-web/home",
            component_key="site_builder.pc_web.home",
            show_in_sidebar=True,
            sort_order=20,
            status="connected",
            is_active=True,
        ),
        SimpleNamespace(
            page_code="site_builder.pc_web",
            title="PC Web",
            parent_code=None,
            level=1,
            route_path="/pc-web",
            component_key="layout.group",
            show_in_sidebar=True,
            sort_order=20,
            status="connected",
            is_active=True,
        ),
    ]

    response = build_navigation_response(pages)

    assert response.app_code == "d2c-site-builder"
    assert len(response.pages) == 1
    assert response.pages[0].page_code == "site_builder.pc_web"
    assert response.pages[0].children[0].page_code == "site_builder.pc_web.home"
