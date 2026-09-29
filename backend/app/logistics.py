from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ShipmentStatus(StrEnum):
    DRAFT = "draft"
    PENDING_OWNER_DECISION = "pending_owner_decision"
    LABEL_READY = "label_ready"
    HANDED_TO_CARRIER = "handed_to_carrier"
    DELIVERED = "delivered"
    BLOCKED = "blocked"


class DeliveryMode(StrEnum):
    SCHOOL_DROP = "school_drop"
    COOPERATIVE_PICKUP = "cooperative_pickup"
    LOCKER = "locker"
    VENDING_MACHINE = "vending_machine"
    HOME_DELIVERY = "home_delivery"


class ShipmentDraft(BaseModel):
    shipment_id: UUID
    organization_id: UUID
    order_reference: str
    carrier_code: str = Field(min_length=2)
    delivery_mode: DeliveryMode
    recipient_scope_id: UUID
    pickup_device_id: UUID | None = None
    parcel_count: int = Field(default=1, ge=1)
    weight_grams: int | None = Field(default=None, ge=0)
    status: ShipmentStatus = ShipmentStatus.DRAFT
    tracking_number: str | None = None
    idempotency_key: str = Field(min_length=8)


class ShipmentLabelResult(BaseModel):
    shipment_id: UUID
    status: ShipmentStatus
    tracking_number: str | None = None
    label_reference: str | None = None
    formal_side_effects: bool = False
