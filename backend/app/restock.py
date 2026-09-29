from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class RestockStatus(StrEnum):
    REQUESTED = "requested"
    AUTHORIZED = "authorized"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    RECONCILIATION_REQUIRED = "reconciliation_required"


class SupplierRestockRequest(BaseModel):
    request_id: UUID
    organization_id: UUID
    supplier_id: UUID
    device_id: UUID | None = None
    location_id: UUID
    requested_by: UUID
    status: RestockStatus = RestockStatus.REQUESTED
    requested_at_utc: datetime
    idempotency_key: str = Field(min_length=8)
    items: list[dict[str, str | int]] = Field(min_length=1)
    proof_reference: str | None = None


class RestockApproval(BaseModel):
    request_id: UUID
    organization_id: UUID
    approved_by: UUID
    approved_at_utc: datetime
    approved: bool
    reason_code: str | None = None
