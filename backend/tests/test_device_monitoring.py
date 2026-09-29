from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.device_monitoring import (
    AlertType,
    ConnectivityStatus,
    DeviceTelemetry,
    evaluate_telemetry,
)
from app.main import app

client = TestClient(app)
HEADERS = {"X-Demo-Mode": "true"}


def test_low_stock_generates_alert_and_restock_request() -> None:
    telemetry = DeviceTelemetry(
        telemetry_id=uuid4(), organization_id=uuid4(), device_id=uuid4(), supplier_id=uuid4(), sku="sku", quantity_available=1,
        low_stock_threshold=5, connectivity=ConnectivityStatus.ONLINE, temperature_celsius=4,
        reported_at_utc=datetime.now(timezone.utc), idempotency_key="telemetry-001",
    )
    result = evaluate_telemetry(telemetry)
    assert any(alert.alert_type == AlertType.LOW_STOCK for alert in result.alerts)
    assert result.auto_restock_request is not None
    assert result.auto_restock_request.status == "requested"


def test_telemetry_api_reports_offline_and_temperature_alerts() -> None:
    telemetry = {
        "telemetry_id": str(uuid4()), "organization_id": str(uuid4()), "device_id": str(uuid4()), "supplier_id": None,
        "sku": "sku", "quantity_available": 20, "low_stock_threshold": 5, "connectivity": "offline",
        "temperature_celsius": 80, "reported_at_utc": datetime.now(timezone.utc).isoformat(), "idempotency_key": "telemetry-002",
    }
    response = client.post("/api/v1/mock/device-monitoring/telemetry", json=telemetry, headers=HEADERS)
    assert response.status_code == 200
    types = {item["alert_type"] for item in response.json()["alerts"]}
    assert {"offline", "temperature"}.issubset(types)


def test_duplicate_telemetry_is_rejected() -> None:
    telemetry = {
        "telemetry_id": str(uuid4()), "organization_id": str(uuid4()), "device_id": str(uuid4()), "supplier_id": None,
        "sku": "sku", "quantity_available": 10, "low_stock_threshold": 2, "connectivity": "online",
        "temperature_celsius": 4, "reported_at_utc": datetime.now(timezone.utc).isoformat(), "idempotency_key": "telemetry-003",
    }
    assert client.post("/api/v1/mock/device-monitoring/telemetry", json=telemetry, headers=HEADERS).status_code == 200
    assert client.post("/api/v1/mock/device-monitoring/telemetry", json=telemetry, headers=HEADERS).status_code == 409


def test_monitoring_requires_demo_header() -> None:
    telemetry = {
        "telemetry_id": str(uuid4()), "organization_id": str(uuid4()), "device_id": str(uuid4()), "supplier_id": None,
        "sku": "sku", "quantity_available": 1, "low_stock_threshold": 2, "connectivity": "online",
        "temperature_celsius": 4, "reported_at_utc": datetime.now(timezone.utc).isoformat(), "idempotency_key": "telemetry-004",
    }
    assert client.post("/api/v1/mock/device-monitoring/telemetry", json=telemetry).status_code == 403
