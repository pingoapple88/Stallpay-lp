CREATE TABLE IF NOT EXISTS external_integrations (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    kind TEXT NOT NULL,
    provider_code TEXT NOT NULL,
    environment TEXT NOT NULL CHECK (environment IN ('sandbox', 'production')),
    status TEXT NOT NULL DEFAULT 'blocked',
    adapter_contract_version TEXT NOT NULL,
    base_url_env_name TEXT NOT NULL,
    credential_ref_names JSONB NOT NULL DEFAULT '[]'::jsonb,
    webhook_path TEXT,
    idempotency_supported BOOLEAN NOT NULL DEFAULT FALSE,
    sandbox_evidence_ref TEXT,
    owner_approval_ref TEXT,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_external_integrations_org_kind_env
    ON external_integrations (organization_id, kind, environment);

-- Secret values and credentials never belong in this table; only environment variable names or secret reference names are stored.
