from uuid import uuid4

from fastapi.testclient import TestClient

from app.integration_readiness import (
    ExternalIntegrationRegistration,
    ExternalServiceKind,
    IntegrationEnvironment,
    IntegrationStatus,
    can_enable_production,
)
from app.main import app

client = TestClient(app)


def test_production_is_blocked_without_owner_approval() -> None:
    registration = ExternalIntegrationRegistration(
        integration_id=uuid4(), organization_id=uuid4(), kind=ExternalServiceKind.LOGISTICS,
        provider_code="mock-carrier", environment=IntegrationEnvironment.PRODUCTION,
        status=IntegrationStatus.OWNER_REVIEW, base_url_env_name="LOGISTICS_BASE_URL",
        credential_ref_names=["LOGISTICS_API_TOKEN"], webhook_path="/webhooks/logistics", idempotency_supported=True,
    )
    assert can_enable_production(registration) is False


def test_production_gate_requires_all_readiness_fields() -> None:
    registration = ExternalIntegrationRegistration(
        integration_id=uuid4(), organization_id=uuid4(), kind=ExternalServiceKind.LOGISTICS,
        provider_code="approved-carrier", environment=IntegrationEnvironment.PRODUCTION,
        status=IntegrationStatus.PRODUCTION_READY, base_url_env_name="LOGISTICS_BASE_URL",
        credential_ref_names=["LOGISTICS_API_TOKEN"], webhook_path="/webhooks/logistics",
        idempotency_supported=True, owner_approval_ref="approval:synthetic-001",
    )
    assert can_enable_production(registration) is True


def test_readiness_api_keeps_sandbox_and_production_separate() -> None:
    body = {
        "integration_id": str(uuid4()), "organization_id": str(uuid4()), "kind": "payment",
        "provider_code": "mock-payment", "environment": "sandbox", "status": "blocked",
        "base_url_env_name": "PAYMENT_BASE_URL", "credential_ref_names": [], "idempotency_supported": False,
    }
    response = client.post("/api/v1/mock/integrations/readiness", json=body, headers={"X-Demo-Mode": "true"})
    assert response.status_code == 200
    assert response.json() == {"can_enable_sandbox": True, "can_enable_production": False}
