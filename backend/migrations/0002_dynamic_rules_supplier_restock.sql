CREATE TABLE IF NOT EXISTS dynamic_rules (
    rule_id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    rule_type TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    status TEXT NOT NULL CHECK (status IN ('draft', 'active', 'suspended', 'expired')),
    cooperative_id UUID,
    supplier_id UUID,
    device_id UUID,
    sku TEXT,
    campaign_id UUID,
    amount_minor BIGINT CHECK (amount_minor IS NULL OR amount_minor >= 0),
    ratio NUMERIC(12, 8) CHECK (ratio IS NULL OR (ratio >= 0 AND ratio <= 1)),
    currency CHAR(3) NOT NULL DEFAULT 'TWD',
    tax_mode TEXT NOT NULL,
    settlement_cycle TEXT NOT NULL,
    effective_from_utc TIMESTAMPTZ NOT NULL,
    effective_to_utc TIMESTAMPTZ,
    priority INTEGER NOT NULL DEFAULT 100,
    approved_by UUID,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (amount_minor IS NOT NULL OR ratio IS NOT NULL),
    CHECK (effective_to_utc IS NULL OR effective_to_utc > effective_from_utc),
    UNIQUE (organization_id, rule_type, version)
);

CREATE INDEX IF NOT EXISTS ix_dynamic_rules_lookup
    ON dynamic_rules (organization_id, rule_type, status, effective_from_utc);

CREATE TABLE IF NOT EXISTS supplier_restock_requests (
    request_id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    supplier_id UUID NOT NULL,
    device_id UUID,
    location_id UUID NOT NULL,
    requested_by UUID NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('requested', 'authorized', 'in_transit', 'received', 'accepted', 'rejected', 'reconciliation_required')),
    requested_at_utc TIMESTAMPTZ NOT NULL,
    idempotency_key TEXT NOT NULL,
    items JSONB NOT NULL,
    proof_reference TEXT,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS ix_restock_org_status
    ON supplier_restock_requests (organization_id, status, requested_at_utc);

-- Supplier self-restock is only a request/approval workflow here.
-- It does not grant access, change inventory authority, or trigger settlement automatically.
