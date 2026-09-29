from __future__ import annotations

from hashlib import sha256
from typing import Any

from app.adapters.contracts import AdapterResult, ILogisticsProvider, IPaymentProvider


class YundingLogisticsSandboxProvider(ILogisticsProvider):
    """Synthetic provider. No vendor endpoint or customer data is used."""

    def create_label(self, *, organization_id: str, shipment_reference: str) -> AdapterResult:
        token = sha256(f"{organization_id}:{shipment_reference}".encode()).hexdigest()[:14].upper()
        return AdapterResult(
            status="label_ready",
            reference=f"YD-SBX-{token}",
            payload={
                "provider": "yunding-digital",
                "environment": "sandbox",
                "label_reference": f"mock-label:{shipment_reference}",
                "formal_side_effects": False,
            },
        )


class IntellaSandboxProvider(IPaymentProvider):
    """Contract-level Scan2Pay simulator based on public docs; no real encryption keys are used."""

    def __init__(self) -> None:
        self._payments: dict[str, dict[str, Any]] = {}

    def create_payment(self, *, organization_id: str, order_reference: str, amount_minor: int) -> AdapterResult:
        if amount_minor <= 0:
            return AdapterResult(status="blocked", payload={"reason": "amount_must_be_positive"})
        if not order_reference.isalnum() or len(order_reference) > 20:
            return AdapterResult(status="blocked", payload={"reason": "store_order_no_must_be_alphanumeric_max_20"})
        reference = f"INT-SBX-{sha256(f'{organization_id}:{order_reference}'.encode()).hexdigest()[:14].upper()}"
        self._payments[reference] = {
            "organization_id": organization_id,
            "order_reference": order_reference,
            "amount_minor": amount_minor,
            "status": "processing",
        }
        return AdapterResult(
            status="processing",
            reference=reference,
            payload={
                "provider": "intella",
                "service_type": "OLPay",
                "payment_url": f"https://sandbox.invalid/pay/{reference}",
                "formal_side_effects": False,
            },
        )

    def verify(self, *, organization_id: str, payment_reference: str) -> AdapterResult:
        payment = self._payments.get(payment_reference)
        if payment is None or payment["organization_id"] != organization_id:
            return AdapterResult(status="blocked", payload={"reason": "payment_not_found_or_scope_mismatch"})
        return AdapterResult(status=payment["status"], reference=payment_reference, payload={"formal_side_effects": False})

    def handle_callback(self, *, organization_id: str, payload: dict[str, Any]) -> AdapterResult:
        reference = str(payload.get("payment_reference", ""))
        result = str(payload.get("result", ""))
        signature_valid = payload.get("signature_valid") is True
        payment = self._payments.get(reference)
        if payment is None or payment["organization_id"] != organization_id:
            return AdapterResult(status="blocked", payload={"reason": "payment_not_found_or_scope_mismatch"})
        if not signature_valid:
            return AdapterResult(status="blocked", reference=reference, payload={"reason": "invalid_signature"})
        status = "paid" if result == "0000" else "failed"
        payment["status"] = status
        return AdapterResult(status=status, reference=reference, payload={"formal_side_effects": False})
