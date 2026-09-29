from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.commercial import RewardCalculation
from app.device_inventory import DeviceInventoryEvent, DeviceInventoryState, apply_device_event
from app.settlement import SettlementBatch, can_reconcile

router = APIRouter(prefix="/api/v1/mock", tags=["mock"])


class RewardPreviewRequest(BaseModel):
    calculation: RewardCalculation


def require_demo_mode(x_demo_mode: str | None) -> None:
    if x_demo_mode != "true":
        raise HTTPException(status_code=403, detail="mock API requires X-Demo-Mode: true")


@router.post("/rewards/preview", response_model=RewardCalculation)
def reward_preview(request: RewardPreviewRequest, x_demo_mode: str | None = Header(default=None)) -> RewardCalculation:
    require_demo_mode(x_demo_mode)
    return request.calculation


@router.post("/device-inventory/apply", response_model=DeviceInventoryState)
def device_inventory_apply(
    state: DeviceInventoryState,
    event: DeviceInventoryEvent,
    x_demo_mode: str | None = Header(default=None),
) -> DeviceInventoryState:
    require_demo_mode(x_demo_mode)
    try:
        return apply_device_event(state, event)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/settlements/reconcile-preview")
def settlement_reconcile_preview(
    batch: SettlementBatch,
    x_demo_mode: str | None = Header(default=None),
) -> dict[str, bool | str]:
    require_demo_mode(x_demo_mode)
    allowed = can_reconcile(batch)
    return {
        "status": "ready_for_review" if allowed else "blocked",
        "can_reconcile": allowed,
        "formal_side_effects": False,
    }
