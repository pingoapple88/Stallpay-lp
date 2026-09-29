from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
HEADERS = {"X-UAT-Mode": "isolated"}


def test_logistics_uat_creates_synthetic_label() -> None:
    response = client.post(
        "/api/v1/uat/logistics/labels",
        json={"organization_id": str(uuid4()), "shipment_reference": "SHIPUAT001"},
        headers=HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "label_ready"
    assert body["reference"].startswith("YD-SBX-")
    assert body["payload"]["formal_side_effects"] is False


def test_intella_uat_payment_callback_and_query() -> None:
    organization_id = str(uuid4())
    created = client.post(
        "/api/v1/uat/payments",
        json={"organization_id": organization_id, "order_reference": "PAYUAT001", "amount_minor": 100},
        headers=HEADERS,
    )
    assert created.status_code == 200
    reference = created.json()["reference"]
    assert created.json()["status"] == "processing"
    callback = client.post(
        f"/api/v1/uat/payments/{reference}/callback",
        json={"organization_id": organization_id, "result": "0000", "signature_valid": True},
        headers=HEADERS,
    )
    assert callback.status_code == 200
    assert callback.json()["status"] == "paid"
    queried = client.get(
        f"/api/v1/uat/payments/{reference}", params={"organization_id": organization_id}, headers=HEADERS
    )
    assert queried.status_code == 200
    assert queried.json()["status"] == "paid"


def test_invalid_signature_fails_closed() -> None:
    organization_id = str(uuid4())
    created = client.post(
        "/api/v1/uat/payments",
        json={"organization_id": organization_id, "order_reference": "PAYUAT002", "amount_minor": 200},
        headers=HEADERS,
    )
    reference = created.json()["reference"]
    callback = client.post(
        f"/api/v1/uat/payments/{reference}/callback",
        json={"organization_id": organization_id, "result": "0000", "signature_valid": False},
        headers=HEADERS,
    )
    assert callback.json()["status"] == "blocked"
    assert callback.json()["payload"]["reason"] == "invalid_signature"


def test_uat_requires_isolated_header() -> None:
    response = client.post(
        "/api/v1/uat/logistics/labels",
        json={"organization_id": str(uuid4()), "shipment_reference": "SHIPUAT002"},
    )
    assert response.status_code == 403


def test_uat_console_is_served_with_three_languages() -> None:
    response = client.get("/uat/")
    assert response.status_code == 200
    assert "校鮮集外部服務測試台" in response.text
    assert "Xiaoxianji External Service UAT" in response.text
    assert "ระบบทดสอบบริการภายนอก Xiaoxianji" in response.text
    config = client.get("/uat/config.js")
    assert config.status_code == 200
    assert 'mode: "API_SANDBOX"' in config.text
