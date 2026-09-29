from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class FlowStatus(StrEnum):
    DRAFT = "draft"
    PENDING_OWNER_DECISION = "pending_owner_decision"
    READY_FOR_REVIEW = "ready_for_review"
    RECONCILED = "reconciled"
    BLOCKED = "blocked"


class InvoiceResponsibility(StrEnum):
    ORGANIZATION = "organization"
    COOPERATIVE = "cooperative"
    SUPPLIER = "supplier"
    THIRD_PARTY = "third_party"
    OWNER_DEFINED = "owner_defined"


class SettlementLine(BaseModel):
    line_id: UUID
    organization_id: UUID
    order_reference: str
    payer_scope_id: UUID
    beneficiary_scope_id: UUID
    amount_minor: int = Field(ge=0)
    currency: str = Field(default="TWD", min_length=3, max_length=3)
    status: FlowStatus = FlowStatus.BLOCKED


class SettlementBatch(BaseModel):
    batch_id: UUID
    organization_id: UUID
    cycle_reference: str
    lines: list[SettlementLine] = Field(default_factory=list)
    invoice_responsibility: InvoiceResponsibility = InvoiceResponsibility.OWNER_DEFINED
    funds_status: FlowStatus = FlowStatus.BLOCKED
    invoice_status: FlowStatus = FlowStatus.BLOCKED
    reconciliation_status: FlowStatus = FlowStatus.BLOCKED
    rule_versions: list[int] = Field(default_factory=list)
    audit_reference: str | None = None


def can_reconcile(batch: SettlementBatch) -> bool:
    """Reconciliation is allowed only when all responsibility fields are explicit."""
    return bool(
        batch.lines
        and batch.invoice_responsibility != InvoiceResponsibility.OWNER_DEFINED
        and batch.funds_status == FlowStatus.READY_FOR_REVIEW
        and batch.invoice_status == FlowStatus.READY_FOR_REVIEW
    )
