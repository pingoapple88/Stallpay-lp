BEGIN;

CREATE TABLE IF NOT EXISTS t7_tianlai_credential_versions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(128) NOT NULL,
    company_ciphertext TEXT NOT NULL,
    token_ciphertext TEXT NOT NULL,
    company_fingerprint VARCHAR(64) NOT NULL,
    token_fingerprint VARCHAR(64) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    source VARCHAR(32) NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_hash VARCHAR(64) NOT NULL,
    previous_version_id VARCHAR(36) NULL REFERENCES t7_tianlai_credential_versions(id),
    CONSTRAINT t7_tianlai_credential_source_check CHECK (source IN ('ENV_BOOTSTRAP', 'MANAGER_UPDATE', 'MANAGER_ROLLBACK'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_t7_tianlai_active_credential
    ON t7_tianlai_credential_versions (tenant_id)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS ix_t7_tianlai_credentials_created_at
    ON t7_tianlai_credential_versions (tenant_id, created_at_utc DESC);

CREATE TABLE IF NOT EXISTS t7_tianlai_audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(128) NOT NULL,
    occurred_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_hash VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL,
    credential_version_id VARCHAR(36) NULL,
    previous_version_id VARCHAR(36) NULL,
    details_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS ix_t7_tianlai_audit_actor_time
    ON t7_tianlai_audit_logs (tenant_id, actor_hash, occurred_at_utc DESC);

CREATE INDEX IF NOT EXISTS ix_t7_tianlai_audit_action_time
    ON t7_tianlai_audit_logs (tenant_id, action, occurred_at_utc DESC);

COMMIT;
