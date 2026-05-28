from typing import Literal

from pydantic import BaseModel, Field

ReadinessLevel = Literal["error", "warning"]
ReadinessStatus = Literal["ready", "blocked", "warning", "empty"]


class PublishReadinessIssueDto(BaseModel):
    level: ReadinessLevel
    code: str
    message: str
    template_region_code: str | None = None
    slot_code: str | None = None
    field_key: str | None = None
    renderer_key: str | None = None


class PublishReadinessSlotDto(BaseModel):
    slot_code: str
    label: str
    renderer_key: str
    required: bool
    status: ReadinessStatus
    is_filled: bool
    issue_count: int = 0
    warning_count: int = 0


class PublishReadinessRegionDto(BaseModel):
    template_region_code: str
    label: str
    required: bool
    status: ReadinessStatus
    issue_count: int = 0
    warning_count: int = 0
    slots: list[PublishReadinessSlotDto] = Field(default_factory=list)


class PublishReadinessSummaryDto(BaseModel):
    region_count: int
    slot_count: int
    required_slot_count: int
    filled_slot_count: int
    issue_count: int
    warning_count: int
    missing_required_slot_count: int


class PublishReadinessResponse(BaseModel):
    site_code: str
    surface_code: str
    page_code: str
    page_title: str
    template_key: str
    template_name: str
    ready: bool
    status: Literal["ready", "blocked"]
    summary: PublishReadinessSummaryDto
    issues: list[PublishReadinessIssueDto] = Field(default_factory=list)
    regions: list[PublishReadinessRegionDto] = Field(default_factory=list)
