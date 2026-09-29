-- Xiaoxianji formal backend baseline.
-- Synthetic/empty environment only until owner-approved deployment is configured.

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending_owner_decision',
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    actor_id UUID,
    event_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    idempotency_key TEXT,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_audit_logs_org_created
    ON audit_logs (organization_id, created_at_utc);

-- No customer, member, order, payment, invoice, ERP, device, or supplier data is seeded here.
