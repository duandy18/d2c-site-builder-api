from datetime import datetime

from pydantic import BaseModel

from app.domains.runtime_contract.contracts.page_contract import RuntimePageContractResponse


class PublishPageRequest(BaseModel):
    published_by: str = "system"


class PublishPageResponse(BaseModel):
    site_code: str
    surface_code: str
    page_code: str
    template_key: str
    publish_version: int
    contract_version: str
    published_by: str
    published_at: datetime
    snapshot: RuntimePageContractResponse
