from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ExternalServiceKind(StrEnum):
    LOGISTICS = "logistics"
    PAYMENT = "payment"
    INVOICE = "invoice"
    ERP = "erp"
    NOTIFICATION = "notification"


class IntegrationEnvironment(StrEnum):
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class IntegrationStatus(StrEnum):
    BLOCKED = "blocked"
    OWNER_REVIEW = "owner_review"
    SANDBOX_READY = "sandbox_ready"
    PRODUCTION_READY = "production_ready"


class ExternalIntegrationRegistration(BaseModel):
    integration_id: UUID
    organization_id: UUID
    kind: ExternalServiceKind
    provider_code: str = Field(min_length=2)
    environment: IntegrationEnvironment
    status: IntegrationStatus = IntegrationStatus.BLOCKED
    adapter_contract_version: str = "v1"
    base_url_env_name: str
    credential_ref_names: list[str] = Field(default_factory=list)
    webhook_path: str | None = None
    idempotency_supported: bool = False
    sandbox_evidence_ref: str | None = None
    owner_approval_ref: str | None = None


def can_enable_production(registration: ExternalIntegrationRegistration) -> bool:
    return bool(
        registration.environment == IntegrationEnvironment.PRODUCTION
        and registration.status == IntegrationStatus.PRODUCTION_READY
        and registration.owner_approval_ref
        and registration.idempotency_supported
        and registration.webhook_path
        and registration.credential_ref_names
    )
