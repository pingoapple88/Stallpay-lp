from uuid import UUID

from fastapi import APIRouter, Header, HTTPException

from app.device_monitoring import DeviceAlert, DeviceTelemetry, MonitoringResult, evaluate_telemetry

router = APIRouter(prefix="/api/v1/mock/device-monitoring", tags=["mock-device-monitoring"])
_RESULTS: dict[UUID, MonitoringResult] = {}
_ALERTS: dict[UUID, DeviceAlert] = {}


def require_demo(x_demo_mode: str | None) -> None:
    if x_demo_mode != "true":
        raise HTTPException(status_code=403, detail="device monitoring mock requires X-Demo-Mode: true")


@router.post("/telemetry", response_model=MonitoringResult)
def ingest_telemetry(telemetry: DeviceTelemetry, x_demo_mode: str | None = Header(default=None)) -> MonitoringResult:
    require_demo(x_demo_mode)
    if telemetry.telemetry_id in _RESULTS:
        raise HTTPException(status_code=409, detail="telemetry already processed")
    result = evaluate_telemetry(telemetry)
    _RESULTS[telemetry.telemetry_id] = result
    for alert in result.alerts:
        _ALERTS[alert.alert_id] = alert
    return result


@router.get("/telemetry/{telemetry_id}", response_model=MonitoringResult)
def get_monitoring_result(telemetry_id: UUID, x_demo_mode: str | None = Header(default=None)) -> MonitoringResult:
    require_demo(x_demo_mode)
    result = _RESULTS.get(telemetry_id)
    if result is None:
        raise HTTPException(status_code=404, detail="telemetry not found")
    return result


@router.post("/alerts/{alert_id}/acknowledge", response_model=DeviceAlert)
def acknowledge_alert(alert_id: UUID, x_demo_mode: str | None = Header(default=None)) -> DeviceAlert:
    require_demo(x_demo_mode)
    alert = _ALERTS.get(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="alert not found")
    updated = alert.model_copy(update={"status": "acknowledged"})
    _ALERTS[alert_id] = updated
    return updated
