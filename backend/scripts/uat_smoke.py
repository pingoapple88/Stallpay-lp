#!/usr/bin/env python3
import json
import sys
from uuid import uuid4

import httpx


def main() -> int:
    base_url = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
    headers = {"X-UAT-Mode": "isolated"}
    organization_id = str(uuid4())
    with httpx.Client(base_url=base_url, timeout=10.0, headers=headers) as client:
        health = client.get("/healthz")
        health.raise_for_status()
        label = client.post("/api/v1/uat/logistics/labels", json={"organization_id": organization_id, "shipment_reference": "SHIPUAT001"})
        label.raise_for_status()
        payment = client.post("/api/v1/uat/payments", json={"organization_id": organization_id, "order_reference": "PAYUAT001", "amount_minor": 100})
        payment.raise_for_status()
        payment_reference = payment.json()["reference"]
        callback = client.post(f"/api/v1/uat/payments/{payment_reference}/callback", json={"organization_id": organization_id, "result": "0000", "signature_valid": True})
        callback.raise_for_status()
        query = client.get(f"/api/v1/uat/payments/{payment_reference}", params={"organization_id": organization_id})
        query.raise_for_status()
    result = {
        "health": health.json(),
        "logistics": label.json(),
        "payment_created": payment.json(),
        "payment_callback": callback.json(),
        "payment_queried": query.json(),
    }
    assert result["logistics"]["status"] == "label_ready"
    assert result["payment_queried"]["status"] == "paid"
    assert result["logistics"]["payload"]["formal_side_effects"] is False
    assert result["payment_queried"]["payload"]["formal_side_effects"] is False
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
