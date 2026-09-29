from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
HEADERS = {"X-Demo-Mode": "true"}


def test_create_shipment_and_label_preview() -> None:
    shipment_id = uuid4()
    body = {
        "shipment_id": str(shipment_id), "organization_id": str(uuid4()), "order_reference": "demo-order-001",
        "carrier_code": "mock-carrier", "delivery_mode": "school_drop", "recipient_scope_id": str(uuid4()),
        "parcel_count": 1, "weight_grams": 800, "idempotency_key": "shipment-001",
    }
    created = client.post("/api/v1/mock/logistics/shipments", json=body, headers=HEADERS)
    assert created.status_code == 201
    assert created.json()["status"] == "pending_owner_decision"
    label = client.post(f"/api/v1/mock/logistics/shipments/{shipment_id}/label-preview", headers=HEADERS)
    assert label.status_code == 200
    assert label.json()["status"] == "label_ready"
    assert label.json()["formal_side_effects"] is False


def test_logistics_requires_demo_header() -> None:
    body = {
        "shipment_id": str(uuid4()), "organization_id": str(uuid4()), "order_reference": "demo-order-002",
        "carrier_code": "mock-carrier", "delivery_mode": "locker", "recipient_scope_id": str(uuid4()),
        "idempotency_key": "shipment-002",
    }
    assert client.post("/api/v1/mock/logistics/shipments", json=body).status_code == 403
