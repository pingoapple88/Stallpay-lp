from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.restock import RestockStatus, SupplierRestockRequest
from app.settlement import FlowStatus, SettlementBatch

router = APIRouter(prefix="/api/v1/mock/operations", tags=["mock-operations"])

_RESTOCKS: dict[UUID, SupplierRestockRequest] = {}
_SETTLEMENTS: dict[UUID, SettlementBatch] = {}


class ReviewDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_INFO = "request_info"


class ReviewRequest(BaseModel):
    reviewer_id: UUID
    decision: ReviewDecision
    reason: str = Field(min_length=3)


class SettlementReport(BaseModel):
    batch_id: UUID
    organization_id: UUID
    cycle_reference: str
    line_count: int
    total_amount_minor: int
    funds_status: FlowStatus
    invoice_status: FlowStatus
    reconciliation_status: FlowStatus
    review_required: bool


def _require_demo(x_demo_mode: str | None) -> None:
    if x_demo_mode != "true":
        raise HTTPException(status_code=403, detail="mock operations require X-Demo-Mode: true")


def _review_status(decision: ReviewDecision) -> RestockStatus:
    if decision == ReviewDecision.APPROVE:
        return RestockStatus.AUTHORIZED
    if decision == ReviewDecision.REJECT:
        return RestockStatus.REJECTED
    return RestockStatus.RECONCILIATION_REQUIRED


@router.post("/restock/requests", response_model=SupplierRestockRequest, status_code=201)
def create_restock_request(
    request: SupplierRestockRequest,
    x_demo_mode: str | None = Header(default=None),
) -> SupplierRestockRequest:
    _require_demo(x_demo_mode)
    if request.request_id in _RESTOCKS:
        raise HTTPException(status_code=409, detail="restock request already exists")
    _RESTOCKS[request.request_id] = request
    return request


@router.post("/restock/requests/{request_id}/review", response_model=SupplierRestockRequest)
def review_restock_request(
    request_id: UUID,
    review: ReviewRequest,
    x_demo_mode: str | None = Header(default=None),
) -> SupplierRestockRequest:
    _require_demo(x_demo_mode)
    request = _RESTOCKS.get(request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="restock request not found")
    if request.status not in {RestockStatus.REQUESTED, RestockStatus.RECONCILIATION_REQUIRED}:
        raise HTTPException(status_code=409, detail="restock request is not reviewable")
    updated = request.model_copy(update={"status": _review_status(review.decision), "proof_reference": f"review:{review.reviewer_id}:{review.reason}"})
    _RESTOCKS[request_id] = updated
    return updated


@router.post("/settlements", response_model=SettlementBatch, status_code=201)
def create_settlement_batch(
    batch: SettlementBatch,
    x_demo_mode: str | None = Header(default=None),
) -> SettlementBatch:
    _require_demo(x_demo_mode)
    if batch.batch_id in _SETTLEMENTS:
        raise HTTPException(status_code=409, detail="settlement batch already exists")
    _SETTLEMENTS[batch.batch_id] = batch
    return batch


@router.get("/settlements/{batch_id}/report", response_model=SettlementReport)
def settlement_report(
    batch_id: UUID,
    x_demo_mode: str | None = Header(default=None),
) -> SettlementReport:
    _require_demo(x_demo_mode)
    batch = _SETTLEMENTS.get(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="settlement batch not found")
    return SettlementReport(
        batch_id=batch.batch_id,
        organization_id=batch.organization_id,
        cycle_reference=batch.cycle_reference,
        line_count=len(batch.lines),
        total_amount_minor=sum(line.amount_minor for line in batch.lines),
        funds_status=batch.funds_status,
        invoice_status=batch.invoice_status,
        reconciliation_status=batch.reconciliation_status,
        review_required=(batch.reconciliation_status != FlowStatus.RECONCILED),
    )


@router.post("/settlements/{batch_id}/review", response_model=SettlementBatch)
def review_settlement_batch(
    batch_id: UUID,
    review: ReviewRequest,
    x_demo_mode: str | None = Header(default=None),
) -> SettlementBatch:
    _require_demo(x_demo_mode)
    batch = _SETTLEMENTS.get(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="settlement batch not found")
    if review.decision == ReviewDecision.APPROVE:
        updated = batch.model_copy(update={"reconciliation_status": FlowStatus.RECONCILED, "audit_reference": f"review:{review.reviewer_id}:{review.reason}"})
    else:
        updated = batch.model_copy(update={"reconciliation_status": FlowStatus.BLOCKED, "audit_reference": f"review:{review.reviewer_id}:{review.reason}"})
    _SETTLEMENTS[batch_id] = updated
    return updated
