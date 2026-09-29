CREATE TABLE IF NOT EXISTS device_telemetry (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    device_id UUID NOT NULL,
    supplier_id UUID,
    sku TEXT NOT NULL,
    quantity_available INTEGER NOT NULL CHECK (quantity_available >= 0),
    low_stock_threshold INTEGER NOT NULL CHECK (low_stock_threshold >= 0),
    connectivity TEXT NOT NULL,
    temperature_celsius NUMERIC(8,3),
    reported_at_utc TIMESTAMPTZ NOT NULL,
    idempotency_key TEXT NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS device_alerts (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    device_id UUID NOT NULL,
    sku TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    message TEXT NOT NULL,
    telemetry_id UUID NOT NULL REFERENCES device_telemetry(id),
    restock_request_id UUID,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_device_telemetry_device_time ON device_telemetry (organization_id, device_id, reported_at_utc);
CREATE INDEX IF NOT EXISTS ix_device_alerts_open ON device_alerts (organization_id, device_id, status);

-- This migration records monitoring facts only. It does not operate a real device or authorize financial side effects.
