from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.domain_rules import DynamicRule, RuleScope
from app.restock import SupplierRestockRequest


def test_dynamic_rule_accepts_amount_and_scope() -> None:
    rule = DynamicRule(
        rule_id=uuid4(),
        rule_type="supplier_service_fee",
        version=1,
        scope=RuleScope(organization_id=uuid4(), supplier_id=uuid4()),
        amount_minor=100,
        effective_from_utc=datetime.now(timezone.utc),
    )
    assert rule.amount_minor == 100


def test_dynamic_rule_requires_amount_or_ratio() -> None:
    with pytest.raises(ValueError, match="amount_minor or ratio"):
        DynamicRule(
            rule_id=uuid4(),
            rule_type="invalid",
            version=1,
            scope=RuleScope(organization_id=uuid4()),
            effective_from_utc=datetime.now(timezone.utc),
        )


def test_supplier_restock_requires_idempotency_and_items() -> None:
    request = SupplierRestockRequest(
        request_id=uuid4(),
        organization_id=uuid4(),
        supplier_id=uuid4(),
        location_id=uuid4(),
        requested_by=uuid4(),
        requested_at_utc=datetime.now(timezone.utc),
        idempotency_key="restock-001",
        items=[{"sku": "synthetic-sku", "quantity": 2}],
    )
    assert request.status.value == "requested"
    assert request.items[0]["quantity"] == 2
