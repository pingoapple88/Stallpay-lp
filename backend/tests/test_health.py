from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_governance_is_blocked_by_default() -> None:
    response = client.get("/api/v1/governance/status")
    assert response.status_code == 200
    assert response.json()["formal_service_connected"] is False
    assert "blocked" in response.json()["external_integrations"]
