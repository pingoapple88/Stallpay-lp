from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.commercial import RewardCalculation
from app.device_inventory import (
    DeviceEventStatus,
    DeviceEventType,
    DeviceInventoryEvent,
    DeviceInventoryState,
    apply_device_event,
)
from app.main import app
from app.settlement import FlowStatus, InvoiceResponsibility, SettlementBatch, SettlementLine

client = TestClient(app)


def test_device_restock_then_reserve_then_deduct() -> None:
    org_id, device_id = uuid4(), uuid4()
    state = DeviceInventoryState(organization_id=org_id, device_id=device_id, sku="synthetic-sku", available_quantity=0, reserved_quantity=0)
    common = {"organization_id": org_id, "device_id": device_id, "sku": "synthetic-sku", "quantity": 3, "status": DeviceEventStatus.ACCEPTED}
    state = apply_device_event(state, DeviceInventoryEvent(event_id=uuid4(), event_type=DeviceEventType.INVENTORY_RESTOCKED, idempotency_key="restock-001", **common))
    state = apply_device_event(state, DeviceInventoryEvent(event_id=uuid4(), event_type=DeviceEventType.INVENTORY_RESERVED, idempotency_key="reserve-001", **common))
    state = apply_device_event(state, DeviceInventoryEvent(event_id=uuid4(), event_type=DeviceEventType.INVENTORY_DEDUCTED, idempotency_key="deduct-001", **common))
    assert state.available_quantity == 0
    assert state.reserved_quantity == 0


def test_device_api_requires_demo_header() -> None:
    payload = {
        "state": {"organization_id": str(uuid4()), "device_id": str(uuid4()), "sku": "sku", "available_quantity": 1, "reserved_quantity": 0},
        "event": {"event_id": str(uuid4()), "organization_id": str(uuid4()), "device_id": str(uuid4()), "sku": "sku", "quantity": 1, "event_type": "inventory.restocked", "idempotency_key": "restock-002", "status": "accepted"},
    }
    response = client.post("/api/v1/mock/device-inventory/apply", json=payload)
    assert response.status_code == 403


def test_settlement_preview_stays_blocked_when_invoice_owner_unknown() -> None:
    org_id = uuid4()
    batch = SettlementBatch(
        batch_id=uuid4(),
        organization_id=org_id,
        cycle_reference="synthetic-cycle",
        lines=[SettlementLine(line_id=uuid4(), organization_id=org_id, order_reference="order-1", payer_scope_id=uuid4(), beneficiary_scope_id=uuid4(), amount_minor=100)],
        funds_status=FlowStatus.READY_FOR_REVIEW,
        invoice_status=FlowStatus.READY_FOR_REVIEW,
        reconciliation_status=FlowStatus.BLOCKED,
        invoice_responsibility=InvoiceResponsibility.OWNER_DEFINED,
    )
    response = client.post("/api/v1/mock/settlements/reconcile-preview", json=batch.model_dump(mode="json"), headers={"X-Demo-Mode": "true"})
    assert response.status_code == 200
    assert response.json() == {"status": "blocked", "can_reconcile": False, "formal_side_effects": False}


def test_reward_preview_is_explicitly_mock_only() -> None:
    calculation = RewardCalculation(member_id=uuid4(), organization_id=uuid4(), order_reference="order-1", eligible_minor=100, points=10, rebate_minor=5, rule_version=1)
    response = client.post("/api/v1/mock/rewards/preview", json={"calculation": calculation.model_dump(mode="json")}, headers={"X-Demo-Mode": "true"})
    assert response.status_code == 200
    assert response.json()["rule_version"] == 1
