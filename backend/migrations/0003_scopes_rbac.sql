CREATE TABLE IF NOT EXISTS cooperatives (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending_owner_decision',
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS schools (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    cooperative_id UUID REFERENCES cooperatives(id),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending_owner_decision',
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending_owner_decision',
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    school_id UUID REFERENCES schools(id),
    supplier_id UUID REFERENCES suppliers(id),
    device_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending_owner_decision',
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rbac_bindings (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    principal_id UUID NOT NULL,
    role TEXT NOT NULL,
    scope_type TEXT NOT NULL CHECK (scope_type IN ('organization', 'cooperative', 'school', 'supplier', 'device')),
    scope_id UUID NOT NULL,
    granted_by UUID NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_cooperatives_org ON cooperatives (organization_id);
CREATE INDEX IF NOT EXISTS ix_schools_org ON schools (organization_id);
CREATE INDEX IF NOT EXISTS ix_suppliers_org ON suppliers (organization_id);
CREATE INDEX IF NOT EXISTS ix_devices_org ON devices (organization_id);
CREATE INDEX IF NOT EXISTS ix_rbac_principal_scope ON rbac_bindings (organization_id, principal_id, scope_type, scope_id, active);

-- Scope checks and role permission enforcement belong to the application authorization layer.
-- No production principal, organization, school, supplier, device, or binding is seeded here.
