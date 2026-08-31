from __future__ import annotations

import os
from pathlib import Path

from cryptography.fernet import Fernet

TEST_DB = Path("/tmp/t7_test_adapter.sqlite3")
TEST_DB.unlink(missing_ok=True)

os.environ.update(
    {
        "DATABASE_URL": f"sqlite:///{TEST_DB}",
        "T7_TENANT_ID": "merchcore-stallpay",
        "TIANLAI_API_BASE_URL": "https://api.tenlifeservice.com",
        "TIANLAI_COMPANY": "2000162",
        "TIANLAI_TOKEN": "test-token-bootstrap",
        "T7_TESTER_ACCESS_KEY": "tester-key-for-tests",
        "T7_MANAGER_ACCESS_KEY": "manager-key-for-tests",
        "CREDENTIAL_ENCRYPTION_KEY": Fernet.generate_key().decode("ascii"),
        "AUDIT_HASH_SALT": "audit-salt-for-tests",
        "T7_ALLOWED_ORIGINS": "https://go.stall.merchcore.ai",
    }
)

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.database import AuditLog, Base, CredentialVersion
from app.main import app, database
from app.provider import TianlaiReadOnlyProvider
from app.signing import AsciiSortedSha256SignatureProvider

assert database is not None
database.engine.dispose()
Base.metadata.create_all(database.engine)


def manager_headers() -> dict[str, str]:
    return {"X-T7-Manager-Key": "manager-key-for-tests"}


def get_tester_headers() -> dict[str, str]:
    return {"X-T7-Test-Key": "tester-key-for-tests"}


def test_document_signature_example_matches() -> None:
    provider = AsciiSortedSha256SignatureProvider("TEST")
    signature = provider.sign({"OrderID": "0123456", "MerchantID": "0001"})
    assert signature == "77b21395d6989067806d08c2b070853ad96508e7adcb79549746b90bc9690c48"


def test_health_and_rbac_and_vault(monkeypatch) -> None:
    async def fake_preflight(self, credentials, client_time_utc):
        assert credentials.company in {"2000162", "3000999"}
        assert credentials.token in {"test-token-bootstrap", "replacement-token-value"}
        return {
            "status": "PASS",
            "server_time_utc": "2026-08-31T00:00:00Z",
            "client_time_utc": client_time_utc,
            "clock": {"status": "PASS", "skew_seconds": 0, "allowed_skew_seconds": 300},
            "dns": {"status": "PASS", "addresses_redacted": True},
            "tls": {"status": "PASS", "certificate_verified": True},
            "upstream_host": "api.tenlifeservice.com",
            "credential_version_id": credentials.version_id,
            "credentials_redacted": True,
            "api_results": [
                {"path": "/Machine.aspx", "method": "GET", "status": "PASS", "query_redacted": True},
                {"path": "/Commodity.aspx", "method": "GET", "status": "PASS", "query_redacted": True},
            ],
            "formal_device_control": False,
            "formal_inventory_write": False,
            "direct_refund": False,
            "unknown_auto_resend": False,
            "test_device_verified": False,
            "completion_signal": False,
            "gate_06": "BLOCKED",
        }

    monkeypatch.setattr(TianlaiReadOnlyProvider, "preflight", fake_preflight)

    with TestClient(app) as client:
        health = client.get("/healthz")
        assert health.status_code == 200
        assert health.json()["credentials_configured"] is True
        assert health.json()["completion_signal"] is False

        assert client.get("/api/v1/t7/settings/status").status_code == 403
        assert client.get("/api/v1/t7/settings/status", headers={"X-T7-Manager-Key": "wrong"}).status_code == 403
        assert client.get("/api/v1/t7/settings/status", headers={"X-T7-Manager-Key": "tester-key-for-tests"}).status_code == 403

        status_response = client.get("/api/v1/t7/settings/status", headers=manager_headers())
        assert status_response.status_code == 200
        initial_status = status_response.json()
        initial_credential = initial_status["credential"]
        initial_version = initial_credential["active_version_id"]
        assert initial_credential["configured"] is True
        assert initial_credential["token_configured"] is True
        assert initial_credential["company_masked"] == "20***62"
        assert "token" not in initial_credential
        serialized = status_response.text.lower()
        assert "test-token-bootstrap" not in serialized
        assert "token_returned" in serialized

        update_response = client.put(
            "/api/v1/t7/settings",
            headers=manager_headers(),
            json={"company": "3000999", "token": "replacement-token-value", "reason": "approved test rotation"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "UPDATED"
        assert update_response.json()["credential"]["token_configured"] is True
        assert "token" not in update_response.json()["credential"]
        updated_version = update_response.json()["active_version_id"]
        assert updated_version != initial_version
        assert "replacement-token-value" not in update_response.text

        with database.session_factory() as session:
            active = session.scalar(
                select(CredentialVersion).where(
                    CredentialVersion.tenant_id == "merchcore-stallpay",
                    CredentialVersion.is_active.is_(True),
                )
            )
            assert active is not None
            assert active.company_ciphertext not in {"3000999", "2000162"}
            assert active.token_ciphertext not in {"replacement-token-value", "test-token-bootstrap"}

        preflight_payload = {
            "run_id": "T7-TEST-001",
            "client_time_utc": "2026-08-31T00:00:00Z",
            "device_role": "cargo_lane_machine",
            "device_id": "test-device-001",
            "site_label": "Tianlai field test",
        }
        assert client.put(
            "/api/v1/t7/settings",
            headers={"X-T7-Manager-Key": "tester-key-for-tests"},
            json={"company": "3000999", "token": "replacement-token-value", "reason": "unauthorized"},
        ).status_code == 403
        assert client.post("/api/v1/t7/network/preflight", json=preflight_payload).status_code == 403
        result = client.post(
            "/api/v1/t7/network/preflight",
            headers=get_tester_headers(),
            json=preflight_payload,
        )
        assert result.status_code == 200
        assert result.json()["status"] == "PASS"
        assert result.json()["completion_signal"] is False
        assert result.json()["gate_06"] == "BLOCKED"
        assert result.json()["test_device_verified"] is False
        response_text = result.text.lower()
        for secret in ("tester-key-for-tests", "manager-key-for-tests", "replacement-token-value", "3000999"):
            assert secret.lower() not in response_text

        rollback_response = client.post(
            "/api/v1/t7/settings/rollback",
            headers=manager_headers(),
            json={"target_version_id": initial_version, "reason": "verified rollback"},
        )
        assert rollback_response.status_code == 200
        assert rollback_response.json()["status"] == "ROLLED_BACK"
        assert "test-token-bootstrap" not in rollback_response.text

        with database.session_factory() as session:
            audit_count = session.scalar(
                select(func.count()).select_from(AuditLog).where(AuditLog.tenant_id == "merchcore-stallpay")
            )
            assert audit_count is not None and audit_count >= 4
            audit_text = "\n".join(
                row.details_json
                for row in session.scalars(
                    select(AuditLog).where(AuditLog.tenant_id == "merchcore-stallpay")
                ).all()
            )
            for secret in ("test-token-bootstrap", "replacement-token-value", "2000162", "3000999"):
                assert secret not in audit_text


def test_tester_cannot_change_credentials() -> None:
    payload = {"company": "9999999", "token": "unauthorized-token", "reason": "must fail"}
    with TestClient(app) as client:
        response = client.put(
            "/api/v1/t7/settings",
            headers={"X-T7-Manager-Key": "tester-key-for-tests"},
            json=payload,
        )
        assert response.status_code == 403
