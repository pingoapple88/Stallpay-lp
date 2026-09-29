from uuid import UUID

from fastapi import APIRouter, Header, HTTPException

from app.logistics import ShipmentDraft, ShipmentLabelResult, ShipmentStatus

router = APIRouter(prefix="/api/v1/mock/logistics", tags=["mock-logistics"])
_SHIPMENTS: dict[UUID, ShipmentDraft] = {}


def require_demo(x_demo_mode: str | None) -> None:
    if x_demo_mode != "true":
        raise HTTPException(status_code=403, detail="logistics mock requires X-Demo-Mode: true")


@router.post("/shipments", response_model=ShipmentDraft, status_code=201)
def create_shipment(draft: ShipmentDraft, x_demo_mode: str | None = Header(default=None)) -> ShipmentDraft:
    require_demo(x_demo_mode)
    if draft.shipment_id in _SHIPMENTS:
        raise HTTPException(status_code=409, detail="shipment already exists")
    _SHIPMENTS[draft.shipment_id] = draft.model_copy(update={"status": ShipmentStatus.PENDING_OWNER_DECISION})
    return _SHIPMENTS[draft.shipment_id]


@router.post("/shipments/{shipment_id}/label-preview", response_model=ShipmentLabelResult)
def create_label_preview(shipment_id: UUID, x_demo_mode: str | None = Header(default=None)) -> ShipmentLabelResult:
    require_demo(x_demo_mode)
    draft = _SHIPMENTS.get(shipment_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="shipment not found")
    if draft.status != ShipmentStatus.PENDING_OWNER_DECISION:
        raise HTTPException(status_code=409, detail="shipment is not ready for label preview")
    updated = draft.model_copy(update={"status": ShipmentStatus.LABEL_READY, "tracking_number": f"DEMO-{shipment_id.hex[:12].upper()}"})
    _SHIPMENTS[shipment_id] = updated
    return ShipmentLabelResult(shipment_id=shipment_id, status=updated.status, tracking_number=updated.tracking_number, label_reference=f"mock-label:{shipment_id}")
