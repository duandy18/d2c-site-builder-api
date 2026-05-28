from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domains.runtime_contract.contracts.page_contract import RuntimePageContractResponse
from app.domains.runtime_contract.services.page_contract import build_runtime_page_contract
from app.domains.site_builder.contracts.publish_snapshot import (
    PublishPageRequest,
    PublishPageResponse,
)
from app.domains.site_builder.models.pc_home import SiteBuilderPublishedPageSnapshot
from app.domains.site_builder.repos.authoring_pages import get_page
from app.domains.site_builder.repos.published_snapshots import (
    add_snapshot,
    clear_current_snapshots,
    get_current_snapshot,
    next_publish_version,
)
from app.domains.site_builder.services.page_authoring_context import (
    require_page_context,
)
from app.domains.site_builder.services.publish_readiness import build_publish_readiness

PUBLISHED_CONTRACT_VERSION = "published-v1"


def publish_page_snapshot(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
    request: PublishPageRequest,
) -> PublishPageResponse:
    readiness = build_publish_readiness(session, site_code, surface_code, page_code)

    if not readiness.ready:
        raise HTTPException(status_code=409, detail="publish_readiness_blocked")

    draft_contract = build_runtime_page_contract(
        session,
        readiness.site_code,
        readiness.surface_code,
        readiness.page_code,
    )
    published_contract = _to_published_contract(draft_contract)
    publish_version = next_publish_version(
        session,
        published_contract.site_code,
        published_contract.surface_code,
        published_contract.page_code,
    )
    published_by = _published_by(request.published_by)

    clear_current_snapshots(
        session,
        published_contract.site_code,
        published_contract.surface_code,
        published_contract.page_code,
    )

    snapshot = SiteBuilderPublishedPageSnapshot(
        site_code=published_contract.site_code,
        surface_code=published_contract.surface_code,
        page_code=published_contract.page_code,
        publish_version=publish_version,
        template_key=published_contract.template_key,
        template_version="v1",
        contract_version=PUBLISHED_CONTRACT_VERSION,
        snapshot_json=published_contract.model_dump(mode="json"),
        readiness_json=readiness.model_dump(mode="json"),
        published_by=published_by,
        is_current=True,
    )
    add_snapshot(session, snapshot)

    page = get_page(
        session,
        published_contract.site_code,
        published_contract.surface_code,
        published_contract.page_code,
    )

    if page is not None:
        page.status = "published"

    session.commit()
    session.refresh(snapshot)

    return PublishPageResponse(
        site_code=snapshot.site_code,
        surface_code=snapshot.surface_code,
        page_code=snapshot.page_code,
        template_key=snapshot.template_key,
        publish_version=snapshot.publish_version,
        contract_version=snapshot.contract_version,
        published_by=snapshot.published_by,
        published_at=snapshot.published_at,
        snapshot=published_contract,
    )


def get_published_runtime_page_contract(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> RuntimePageContractResponse:
    context = require_page_context(session, site_code, surface_code, page_code)
    snapshot = get_current_snapshot(
        session,
        context.site_code,
        context.surface_code,
        context.page_code,
    )

    if snapshot is None:
        raise HTTPException(status_code=404, detail="published_snapshot_not_found")

    return RuntimePageContractResponse.model_validate(snapshot.snapshot_json)


def _to_published_contract(
    draft_contract: RuntimePageContractResponse,
) -> RuntimePageContractResponse:
    return draft_contract.model_copy(
        update={
            "contract_version": PUBLISHED_CONTRACT_VERSION,
            "status": "published",
        }
    )


def _published_by(value: str) -> str:
    normalized = value.strip()

    return normalized or "system"
