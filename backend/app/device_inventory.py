from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceEventType(StrEnum):
    INVENTORY_RESTOCKED = "inventory.restocked"
    INVENTORY_RESERVED = "inventory.reserved"
    INVENTORY_DEDUCTED = "inventory.deducted"
    INVENTORY_EXCEPTION = "inventory.exception"


class DeviceEventStatus(StrEnum):
    ACCEPTED = "accepted"
    BLOCKED = "blocked"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"


class DeviceInventoryEvent(BaseModel):
    event_id: UUID
    organization_id: UUID
    device_id: UUID
    supplier_id: UUID | None = None
    sku: str
    quantity: int = Field(gt=0)
    event_type: DeviceEventType
    idempotency_key: str = Field(min_length=8)
    status: DeviceEventStatus = DeviceEventStatus.BLOCKED
    audit_reference: str | None = None


class DeviceInventoryState(BaseModel):
    organization_id: UUID
    device_id: UUID
    sku: str
    available_quantity: int = Field(ge=0)
    reserved_quantity: int = Field(ge=0)
    last_event_id: UUID | None = None


def apply_device_event(
    state: DeviceInventoryState,
    event: DeviceInventoryEvent,
) -> DeviceInventoryState:
    """Apply only same-scope, accepted events; unknown events remain fail-closed."""
    if event.organization_id != state.organization_id or event.device_id != state.device_id or event.sku != state.sku:
        raise ValueError("scope mismatch")
    if event.status != DeviceEventStatus.ACCEPTED:
        return state
    if event.event_type == DeviceEventType.INVENTORY_RESTOCKED:
        return state.model_copy(update={
            "available_quantity": state.available_quantity + event.quantity,
            "last_event_id": event.event_id,
        })
    if event.event_type == DeviceEventType.INVENTORY_RESERVED:
        if event.quantity > state.available_quantity:
            raise ValueError("insufficient available inventory")
        return state.model_copy(update={
            "available_quantity": state.available_quantity - event.quantity,
            "reserved_quantity": state.reserved_quantity + event.quantity,
            "last_event_id": event.event_id,
        })
    if event.event_type == DeviceEventType.INVENTORY_DEDUCTED:
        if event.quantity > state.reserved_quantity:
            raise ValueError("deduction exceeds reserved inventory")
        return state.model_copy(update={
            "reserved_quantity": state.reserved_quantity - event.quantity,
            "last_event_id": event.event_id,
        })
    return state
