CREATE TABLE IF NOT EXISTS shipment_drafts (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    order_reference TEXT NOT NULL,
    carrier_code TEXT NOT NULL,
    delivery_mode TEXT NOT NULL,
    recipient_scope_id UUID NOT NULL,
    pickup_device_id UUID,
    parcel_count INTEGER NOT NULL DEFAULT 1 CHECK (parcel_count > 0),
    weight_grams INTEGER CHECK (weight_grams IS NULL OR weight_grams >= 0),
    status TEXT NOT NULL DEFAULT 'draft',
    tracking_number TEXT,
    idempotency_key TEXT NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS ix_shipment_drafts_org_status ON shipment_drafts (organization_id, status);

-- Carrier credentials, label purchase, shipment booking, payment and tracking webhooks require a separate approved adapter.
