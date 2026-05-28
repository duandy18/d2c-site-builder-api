from typing import Any

from sqlalchemy.orm import Session

from app.domains.site_builder.contracts.page_content import (
    PageContentSlotDto,
)
from app.domains.site_builder.contracts.publish_readiness import (
    PublishReadinessIssueDto,
    PublishReadinessRegionDto,
    PublishReadinessResponse,
    PublishReadinessSlotDto,
    PublishReadinessSummaryDto,
    ReadinessLevel,
    ReadinessStatus,
)
from app.domains.site_builder.services.page_content import build_page_content_form

IMAGE_MATRIX_SIDE_IMAGES_SLOT = "product.image_matrix.side_images"
IMAGE_MATRIX_MIN_IMAGES = 4
IMAGE_MATRIX_RECOMMENDED_IMAGES = 6


def build_publish_readiness(
    session: Session,
    site_code: str,
    surface_code: str,
    page_code: str,
) -> PublishReadinessResponse:
    form = build_page_content_form(session, site_code, surface_code, page_code)

    all_issues: list[PublishReadinessIssueDto] = []
    region_results: list[PublishReadinessRegionDto] = []
    slot_count = 0
    required_slot_count = 0
    filled_slot_count = 0
    missing_required_slot_codes: set[str] = set()

    for group in form.groups:
        slot_results: list[PublishReadinessSlotDto] = []
        region_issues: list[PublishReadinessIssueDto] = []

        for slot in group.slots:
            slot_count += 1
            if slot.required:
                required_slot_count += 1

            slot_issues = _validate_slot(group.template_region_code, slot)
            all_issues.extend(slot_issues)
            region_issues.extend(slot_issues)

            slot_error_count = _count_by_level(slot_issues, "error")
            slot_warning_count = _count_by_level(slot_issues, "warning")
            slot_is_filled = _slot_is_filled(slot)

            if slot_is_filled:
                filled_slot_count += 1

            if slot.required and slot_error_count > 0:
                missing_required_slot_codes.add(slot.slot_code)

            slot_results.append(
                PublishReadinessSlotDto(
                    slot_code=slot.slot_code,
                    label=slot.label,
                    renderer_key=slot.renderer_key,
                    required=slot.required,
                    status=_slot_status(slot, slot_error_count, slot_warning_count, slot_is_filled),
                    is_filled=slot_is_filled,
                    issue_count=slot_error_count,
                    warning_count=slot_warning_count,
                )
            )

        region_error_count = _count_by_level(region_issues, "error")
        region_warning_count = _count_by_level(region_issues, "warning")

        region_results.append(
            PublishReadinessRegionDto(
                template_region_code=group.template_region_code,
                label=group.label,
                required=group.required,
                status=_region_status(region_error_count, region_warning_count, slot_results),
                issue_count=region_error_count,
                warning_count=region_warning_count,
                slots=slot_results,
            )
        )

    issue_count = _count_by_level(all_issues, "error")
    warning_count = _count_by_level(all_issues, "warning")
    ready = issue_count == 0

    return PublishReadinessResponse(
        site_code=form.site_code,
        surface_code=form.surface_code,
        page_code=form.page_code,
        page_title=form.page_title,
        template_key=form.template_key,
        template_name=form.template_name,
        ready=ready,
        status="ready" if ready else "blocked",
        summary=PublishReadinessSummaryDto(
            region_count=len(form.groups),
            slot_count=slot_count,
            required_slot_count=required_slot_count,
            filled_slot_count=filled_slot_count,
            issue_count=issue_count,
            warning_count=warning_count,
            missing_required_slot_count=len(missing_required_slot_codes),
        ),
        issues=all_issues,
        regions=region_results,
    )


def _validate_slot(
    template_region_code: str,
    slot: PageContentSlotDto,
) -> list[PublishReadinessIssueDto]:
    issues: list[PublishReadinessIssueDto] = []
    fields = _schema_fields(slot.content_schema)
    should_validate_required_fields = (
        slot.required
        or slot.status == "active"
        or _has_content(slot.content)
    )

    if should_validate_required_fields:
        for field_key, field_schema in fields.items():
            if not field_schema.get("required"):
                continue

            value = slot.content.get(field_key)

            if _is_missing(value):
                issues.append(
                    _issue(
                        level="error",
                        code="missing_required_field",
                        message=f"必填字段未填写：{field_key}",
                        template_region_code=template_region_code,
                        slot=slot,
                        field_key=field_key,
                    )
                )
                continue

            if _looks_like_image_field(field_key) and not _has_image_url(value):
                issues.append(
                    _issue(
                        level="error",
                        code="missing_image_url",
                        message=f"图片字段缺少 URL：{field_key}",
                        template_region_code=template_region_code,
                        slot=slot,
                        field_key=field_key,
                    )
                )

    if slot.slot_code == IMAGE_MATRIX_SIDE_IMAGES_SLOT:
        image_count = _count_image_urls(slot.content.get("images"))

        if image_count < IMAGE_MATRIX_MIN_IMAGES:
            issues.append(
                _issue(
                    level="error",
                    code="image_matrix_side_images_min_4",
                    message="多图展示详情页至少需要 4 张多角度图片",
                    template_region_code=template_region_code,
                    slot=slot,
                    field_key="images",
                )
            )
        elif image_count < IMAGE_MATRIX_RECOMMENDED_IMAGES:
            issues.append(
                _issue(
                    level="warning",
                    code="image_matrix_side_images_recommend_6",
                    message="多图展示详情页建议配置 6 张多角度图片",
                    template_region_code=template_region_code,
                    slot=slot,
                    field_key="images",
                )
            )

    return issues


def _schema_fields(schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fields = schema.get("fields")

    if not isinstance(fields, dict):
        return {}

    return {
        field_key: field_schema
        for field_key, field_schema in fields.items()
        if isinstance(field_schema, dict)
    }


def _slot_status(
    slot: PageContentSlotDto,
    error_count: int,
    warning_count: int,
    is_filled: bool,
) -> ReadinessStatus:
    if error_count > 0:
        return "blocked"

    if warning_count > 0:
        return "warning"

    if is_filled or _has_no_content_fields(slot):
        return "ready"

    return "empty"


def _region_status(
    error_count: int,
    warning_count: int,
    slots: list[PublishReadinessSlotDto],
) -> ReadinessStatus:
    if error_count > 0:
        return "blocked"

    if warning_count > 0:
        return "warning"

    if any(slot.status == "ready" for slot in slots):
        return "ready"

    return "empty"


def _slot_is_filled(slot: PageContentSlotDto) -> bool:
    if _has_no_content_fields(slot):
        return True

    return _has_content(slot.content)


def _has_no_content_fields(slot: PageContentSlotDto) -> bool:
    return len(_schema_fields(slot.content_schema)) == 0


def _has_content(content: dict[str, Any]) -> bool:
    return any(not _is_missing(value) for value in content.values())


def _is_missing(value: Any) -> bool:
    if value is None:
        return True

    if isinstance(value, str):
        return len(value.strip()) == 0

    if isinstance(value, list):
        return len(value) == 0

    if isinstance(value, dict):
        return len(value) == 0

    return False


def _looks_like_image_field(field_key: str) -> bool:
    return field_key == "image" or field_key.endswith("_image")


def _has_image_url(value: Any) -> bool:
    if isinstance(value, str):
        return len(value.strip()) > 0

    if not isinstance(value, dict):
        return False

    url = value.get("url")
    if isinstance(url, str) and url.strip():
        return True

    nested_image = value.get("image")
    if nested_image is not None:
        return _has_image_url(nested_image)

    return False


def _count_image_urls(value: Any) -> int:
    if not isinstance(value, list):
        return 0

    return sum(1 for item in value if _has_image_url(item))


def _issue(
    *,
    level: ReadinessLevel,
    code: str,
    message: str,
    template_region_code: str,
    slot: PageContentSlotDto,
    field_key: str,
) -> PublishReadinessIssueDto:
    return PublishReadinessIssueDto(
        level=level,
        code=code,
        message=message,
        template_region_code=template_region_code,
        slot_code=slot.slot_code,
        field_key=field_key,
        renderer_key=slot.renderer_key,
    )


def _count_by_level(issues: list[PublishReadinessIssueDto], level: str) -> int:
    return sum(1 for issue in issues if issue.level == level)
