from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class PriceChannel(StrEnum):
    DIRECT = "direct"
    DEALER = "dealer"
    ENTERPRISE = "enterprise"


class RewardKind(StrEnum):
    POINTS = "points"
    REBATE = "rebate"


class AllocationParty(StrEnum):
    PLATFORM = "platform"
    COOPERATIVE = "cooperative"
    SCHOOL = "school"
    SUPPLIER = "supplier"
    DEVICE_OWNER = "device_owner"


class PricingRule(BaseModel):
    rule_id: UUID
    organization_id: UUID
    sku: str
    channel: PriceChannel
    amount_minor: int = Field(ge=0)
    currency: str = Field(default="TWD", min_length=3, max_length=3)
    tax_mode: str = "owner_defined"
    version: int = Field(ge=1)
    active: bool = False


class RewardRule(BaseModel):
    rule_id: UUID
    organization_id: UUID
    cooperative_id: UUID | None = None
    kind: RewardKind
    points_per_minor: Decimal | None = Field(default=None, ge=0)
    rebate_ratio: Decimal | None = Field(default=None, ge=0, le=1)
    version: int = Field(ge=1)
    active: bool = False

    @model_validator(mode="after")
    def require_formula(self) -> "RewardRule":
        if self.points_per_minor is None and self.rebate_ratio is None:
            raise ValueError("points_per_minor or rebate_ratio is required")
        return self


class ProfitAllocationRule(BaseModel):
    rule_id: UUID
    organization_id: UUID
    beneficiary: AllocationParty
    ratio: Decimal = Field(ge=0, le=1)
    version: int = Field(ge=1)
    active: bool = False


class RewardCalculation(BaseModel):
    member_id: UUID
    organization_id: UUID
    order_reference: str
    eligible_minor: int = Field(ge=0)
    points: int = Field(ge=0)
    rebate_minor: int = Field(ge=0)
    rule_version: int
