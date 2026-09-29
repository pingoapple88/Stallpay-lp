from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class RuleStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class TaxMode(StrEnum):
    TAX_INCLUDED = "tax_included"
    TAX_EXCLUDED = "tax_excluded"
    TAX_ADDED = "tax_added"
    OWNER_DEFINED = "owner_defined"


class SettlementCycle(StrEnum):
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CAMPAIGN = "campaign"
    CUSTOM = "custom"


class RuleScope(BaseModel):
    organization_id: UUID
    cooperative_id: UUID | None = None
    supplier_id: UUID | None = None
    device_id: UUID | None = None
    sku: str | None = None
    campaign_id: UUID | None = None


class DynamicRule(BaseModel):
    rule_id: UUID
    rule_type: str = Field(min_length=1)
    version: int = Field(ge=1)
    status: RuleStatus = RuleStatus.DRAFT
    scope: RuleScope
    amount_minor: int | None = Field(default=None, ge=0)
    ratio: Decimal | None = Field(default=None, ge=0, le=1)
    currency: str = Field(default="TWD", min_length=3, max_length=3)
    tax_mode: TaxMode = TaxMode.OWNER_DEFINED
    settlement_cycle: SettlementCycle = SettlementCycle.CUSTOM
    effective_from_utc: datetime
    effective_to_utc: datetime | None = None
    priority: int = Field(default=100, ge=0)
    approved_by: UUID | None = None

    @model_validator(mode="after")
    def validate_period(self) -> "DynamicRule":
        if self.effective_to_utc and self.effective_to_utc <= self.effective_from_utc:
            raise ValueError("effective_to_utc must be after effective_from_utc")
        if self.amount_minor is None and self.ratio is None:
            raise ValueError("amount_minor or ratio is required")
        return self
