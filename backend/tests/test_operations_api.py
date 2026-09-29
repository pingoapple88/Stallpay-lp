from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
HEADERS = {"X-Demo-Mode": "true"}


def test_restock_request_and_manual_approval() -> None:
    org_id, supplier_id, location_id = uuid4(), uuid4(), uuid4()
    request_id = uuid4()
    body = {
        "request_id": str(request_id), "organization_id": str(org_id), "supplier_id": str(supplier_id),
        "location_id": str(location_id), "requested_by": str(uuid4()), "requested_at_utc": datetime.now(timezone.utc).isoformat(),
        "idempotency_key": "api-restock-001", "items": [{"sku": "synthetic-sku", "quantity": 4}],
    }
    created = client.post("/api/v1/mock/operations/restock/requests", json=body, headers=HEADERS)
    assert created.status_code == 201
    reviewed = client.post(
        f"/api/v1/mock/operations/restock/requests/{request_id}/review",
        json={"reviewer_id": str(uuid4()), "decision": "approve", "reason": "庫存與補貨證明已核對"}, headers=HEADERS,
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "authorized"


def test_settlement_report_and_review() -> None:
    org_id, batch_id = uuid4(), uuid4()
    body = {
        "batch_id": str(batch_id), "organization_id": str(org_id), "cycle_reference": "api-cycle-001",
        "lines": [{"line_id": str(uuid4()), "organization_id": str(org_id), "order_reference": "order-1", "payer_scope_id": str(uuid4()), "beneficiary_scope_id": str(uuid4()), "amount_minor": 2500, "status": "blocked"}],
        "invoice_responsibility": "owner_defined", "funds_status": "blocked", "invoice_status": "blocked", "reconciliation_status": "blocked", "rule_versions": [1],
    }
    created = client.post("/api/v1/mock/operations/settlements", json=body, headers=HEADERS)
    assert created.status_code == 201
    report = client.get(f"/api/v1/mock/operations/settlements/{batch_id}/report", headers=HEADERS)
    assert report.status_code == 200
    assert report.json()["total_amount_minor"] == 2500
    reviewed = client.post(f"/api/v1/mock/operations/settlements/{batch_id}/review", json={"reviewer_id": str(uuid4()), "decision": "approve", "reason": "人工覆核完成"}, headers=HEADERS)
    assert reviewed.status_code == 200
    assert reviewed.json()["reconciliation_status"] == "reconciled"


def test_operations_api_rejects_without_demo_header() -> None:
    response = client.get(f"/api/v1/mock/operations/settlements/{uuid4()}/report")
    assert response.status_code == 403
