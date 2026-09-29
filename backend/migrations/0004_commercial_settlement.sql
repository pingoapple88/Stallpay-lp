CREATE TABLE IF NOT EXISTS pricing_rules (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    sku TEXT NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('direct', 'dealer', 'enterprise')),
    amount_minor BIGINT NOT NULL CHECK (amount_minor >= 0),
    currency CHAR(3) NOT NULL DEFAULT 'TWD',
    tax_mode TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, sku, channel, version)
);

CREATE TABLE IF NOT EXISTS reward_rules (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    cooperative_id UUID,
    kind TEXT NOT NULL CHECK (kind IN ('points', 'rebate')),
    points_per_minor NUMERIC(18,8),
    rebate_ratio NUMERIC(12,8) CHECK (rebate_ratio IS NULL OR (rebate_ratio >= 0 AND rebate_ratio <= 1)),
    version INTEGER NOT NULL CHECK (version > 0),
    active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (points_per_minor IS NOT NULL OR rebate_ratio IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS profit_allocation_rules (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    beneficiary TEXT NOT NULL,
    ratio NUMERIC(12,8) NOT NULL CHECK (ratio >= 0 AND ratio <= 1),
    version INTEGER NOT NULL CHECK (version > 0),
    active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS settlement_batches (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    cycle_reference TEXT NOT NULL,
    invoice_responsibility TEXT NOT NULL DEFAULT 'owner_defined',
    funds_status TEXT NOT NULL DEFAULT 'blocked',
    invoice_status TEXT NOT NULL DEFAULT 'blocked',
    reconciliation_status TEXT NOT NULL DEFAULT 'blocked',
    rule_versions JSONB NOT NULL DEFAULT '[]'::jsonb,
    audit_reference TEXT,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS settlement_lines (
    id UUID PRIMARY KEY,
    batch_id UUID NOT NULL REFERENCES settlement_batches(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    order_reference TEXT NOT NULL,
    payer_scope_id UUID NOT NULL,
    beneficiary_scope_id UUID NOT NULL,
    amount_minor BIGINT NOT NULL CHECK (amount_minor >= 0),
    currency CHAR(3) NOT NULL DEFAULT 'TWD',
    status TEXT NOT NULL DEFAULT 'blocked'
);

CREATE INDEX IF NOT EXISTS ix_pricing_rules_org_sku ON pricing_rules (organization_id, sku, channel, active);
CREATE INDEX IF NOT EXISTS ix_reward_rules_org ON reward_rules (organization_id, active);
CREATE INDEX IF NOT EXISTS ix_settlement_batches_org ON settlement_batches (organization_id, cycle_reference);
CREATE INDEX IF NOT EXISTS ix_settlement_lines_batch ON settlement_lines (batch_id, organization_id);

-- No payment, invoice issuance, tax filing, payout, or accounting side effect is performed by this migration.
