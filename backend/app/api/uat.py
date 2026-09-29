from uuid import UUID

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.adapters.contracts import AdapterResult
from app.adapters.sandbox_providers import IntellaSandboxProvider, YundingLogisticsSandboxProvider

router = APIRouter(prefix="/api/v1/uat", tags=["isolated-uat"])
_logistics = YundingLogisticsSandboxProvider()
_payment = IntellaSandboxProvider()


class LogisticsUatRequest(BaseModel):
    organization_id: UUID
    shipment_reference: str = Field(min_length=3)


class PaymentUatRequest(BaseModel):
    organization_id: UUID
    order_reference: str = Field(min_length=1, max_length=20, pattern=r"^[A-Za-z0-9]+$")
    amount_minor: int = Field(gt=0)


class PaymentCallbackUatRequest(BaseModel):
    organization_id: UUID
    result: str = Field(pattern=r"^(0000|9999)$")
    signature_valid: bool


def require_uat(x_uat_mode: str | None) -> None:
    if x_uat_mode != "isolated":
        raise HTTPException(status_code=403, detail="isolated UAT requires X-UAT-Mode: isolated")


@router.post("/logistics/labels", response_model=AdapterResult)
def create_logistics_label(request: LogisticsUatRequest, x_uat_mode: str | None = Header(default=None)) -> AdapterResult:
    require_uat(x_uat_mode)
    return _logistics.create_label(organization_id=str(request.organization_id), shipment_reference=request.shipment_reference)


@router.post("/payments", response_model=AdapterResult)
def create_payment(request: PaymentUatRequest, x_uat_mode: str | None = Header(default=None)) -> AdapterResult:
    require_uat(x_uat_mode)
    return _payment.create_payment(organization_id=str(request.organization_id), order_reference=request.order_reference, amount_minor=request.amount_minor)


@router.get("/payments/{payment_reference}", response_model=AdapterResult)
def query_payment(payment_reference: str, organization_id: UUID, x_uat_mode: str | None = Header(default=None)) -> AdapterResult:
    require_uat(x_uat_mode)
    return _payment.verify(organization_id=str(organization_id), payment_reference=payment_reference)


@router.post("/payments/{payment_reference}/callback", response_model=AdapterResult)
def simulate_payment_callback(payment_reference: str, request: PaymentCallbackUatRequest, x_uat_mode: str | None = Header(default=None)) -> AdapterResult:
    require_uat(x_uat_mode)
    return _payment.handle_callback(
        organization_id=str(request.organization_id),
        payload={"payment_reference": payment_reference, "result": request.result, "signature_valid": request.signature_valid},
    )
