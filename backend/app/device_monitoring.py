from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.restock import RestockStatus, SupplierRestockRequest


class ConnectivityStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class AlertType(StrEnum):
    LOW_STOCK = "low_stock"
    OFFLINE = "offline"
    TEMPERATURE = "temperature"
    INVENTORY_MISMATCH = "inventory_mismatch"


class AlertStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    BLOCKED = "blocked"


class DeviceTelemetry(BaseModel):
    telemetry_id: UUID
    organization_id: UUID
    device_id: UUID
    supplier_id: UUID | None = None
    sku: str
    quantity_available: int = Field(ge=0)
    low_stock_threshold: int = Field(ge=0)
    connectivity: ConnectivityStatus
    temperature_celsius: float | None = None
    reported_at_utc: datetime
    idempotency_key: str = Field(min_length=8)


class DeviceAlert(BaseModel):
    alert_id: UUID
    organization_id: UUID
    device_id: UUID
    sku: str
    alert_type: AlertType
    status: AlertStatus = AlertStatus.OPEN
    message: str
    telemetry_id: UUID
    created_at_utc: datetime
    restock_request_id: UUID | None = None


class MonitoringResult(BaseModel):
    telemetry: DeviceTelemetry
    alerts: list[DeviceAlert] = Field(default_factory=list)
    auto_restock_request: SupplierRestockRequest | None = None


def evaluate_telemetry(telemetry: DeviceTelemetry) -> MonitoringResult:
    alerts: list[DeviceAlert] = []
    now = datetime.now(timezone.utc)
    if telemetry.quantity_available <= telemetry.low_stock_threshold:
        alerts.append(DeviceAlert(
            alert_id=uuid4(), organization_id=telemetry.organization_id, device_id=telemetry.device_id,
            sku=telemetry.sku, alert_type=AlertType.LOW_STOCK,
            message="庫存低於可配置門檻，已建立補貨待辦", telemetry_id=telemetry.telemetry_id, created_at_utc=now,
        ))
    if telemetry.connectivity != ConnectivityStatus.ONLINE:
        alerts.append(DeviceAlert(
            alert_id=uuid4(), organization_id=telemetry.organization_id, device_id=telemetry.device_id,
            sku=telemetry.sku, alert_type=AlertType.OFFLINE,
            message="設備連線狀態非 ONLINE，停止自動設備操作", telemetry_id=telemetry.telemetry_id, created_at_utc=now,
        ))
    if telemetry.temperature_celsius is not None and not (-5 <= telemetry.temperature_celsius <= 45):
        alerts.append(DeviceAlert(
            alert_id=uuid4(), organization_id=telemetry.organization_id, device_id=telemetry.device_id,
            sku=telemetry.sku, alert_type=AlertType.TEMPERATURE,
            message="溫度超出展示安全範圍，轉人工確認", telemetry_id=telemetry.telemetry_id, created_at_utc=now,
        ))
    restock = None
    low_stock = any(alert.alert_type == AlertType.LOW_STOCK for alert in alerts)
    if low_stock and telemetry.supplier_id:
        restock = SupplierRestockRequest(
            request_id=uuid4(), organization_id=telemetry.organization_id, supplier_id=telemetry.supplier_id,
            device_id=telemetry.device_id, location_id=telemetry.device_id, requested_by=telemetry.device_id,
            status=RestockStatus.REQUESTED, requested_at_utc=now,
            idempotency_key=f"auto-restock-{telemetry.telemetry_id}",
            items=[{"sku": telemetry.sku, "quantity": max(telemetry.low_stock_threshold * 2, 1)}],
            proof_reference=f"telemetry:{telemetry.telemetry_id}",
        )
        for alert in alerts:
            if alert.alert_type == AlertType.LOW_STOCK:
                alert.restock_request_id = restock.request_id
    return MonitoringResult(telemetry=telemetry, alerts=alerts, auto_restock_request=restock)
