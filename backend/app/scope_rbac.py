from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ScopeType(StrEnum):
    ORGANIZATION = "organization"
    COOPERATIVE = "cooperative"
    SCHOOL = "school"
    SUPPLIER = "supplier"
    DEVICE = "device"


class EntityStatus(StrEnum):
    PENDING_OWNER_DECISION = "pending_owner_decision"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class RbacRole(StrEnum):
    ORGANIZATION_ADMIN = "organization_admin"
    COOPERATIVE_MANAGER = "cooperative_manager"
    SCHOOL_COORDINATOR = "school_coordinator"
    SUPPLIER_OPERATOR = "supplier_operator"
    DEVICE_OPERATOR = "device_operator"
    FINANCE_REVIEWER = "finance_reviewer"
    ORDER_REVIEWER = "order_reviewer"
    READ_ONLY_AUDITOR = "read_only_auditor"


class Permission(StrEnum):
    SCOPE_READ = "scope.read"
    MEMBER_READ = "member.read"
    ORDER_READ = "order.read"
    ORDER_REVIEW = "order.review"
    INVENTORY_READ = "inventory.read"
    INVENTORY_RESTOCK_REQUEST = "inventory.restock_request"
    DEVICE_READ = "device.read"
    DEVICE_OPERATE = "device.operate"
    FINANCE_READ = "finance.read"
    FINANCE_RECONCILE = "finance.reconcile"
    RBAC_MANAGE = "rbac.manage"
    AUDIT_READ = "audit.read"


ROLE_PERMISSIONS: dict[RbacRole, frozenset[Permission]] = {
    RbacRole.ORGANIZATION_ADMIN: frozenset(Permission),
    RbacRole.COOPERATIVE_MANAGER: frozenset({
        Permission.SCOPE_READ, Permission.MEMBER_READ, Permission.ORDER_READ,
        Permission.INVENTORY_READ, Permission.INVENTORY_RESTOCK_REQUEST,
        Permission.FINANCE_READ, Permission.FINANCE_RECONCILE, Permission.AUDIT_READ,
    }),
    RbacRole.SCHOOL_COORDINATOR: frozenset({
        Permission.SCOPE_READ, Permission.MEMBER_READ, Permission.ORDER_READ,
        Permission.INVENTORY_READ, Permission.AUDIT_READ,
    }),
    RbacRole.SUPPLIER_OPERATOR: frozenset({
        Permission.SCOPE_READ, Permission.INVENTORY_READ,
        Permission.INVENTORY_RESTOCK_REQUEST, Permission.AUDIT_READ,
    }),
    RbacRole.DEVICE_OPERATOR: frozenset({
        Permission.SCOPE_READ, Permission.DEVICE_READ,
        Permission.DEVICE_OPERATE, Permission.INVENTORY_READ, Permission.AUDIT_READ,
    }),
    RbacRole.FINANCE_REVIEWER: frozenset({
        Permission.SCOPE_READ, Permission.FINANCE_READ,
        Permission.FINANCE_RECONCILE, Permission.AUDIT_READ,
    }),
    RbacRole.ORDER_REVIEWER: frozenset({
        Permission.SCOPE_READ, Permission.ORDER_READ,
        Permission.ORDER_REVIEW, Permission.AUDIT_READ,
    }),
    RbacRole.READ_ONLY_AUDITOR: frozenset({
        Permission.SCOPE_READ, Permission.AUDIT_READ,
    }),
}


class OrganizationScope(BaseModel):
    organization_id: UUID
    company_id: UUID | None = None
    status: EntityStatus = EntityStatus.PENDING_OWNER_DECISION


class CooperativeScope(BaseModel):
    cooperative_id: UUID
    organization_id: UUID
    status: EntityStatus = EntityStatus.PENDING_OWNER_DECISION


class SchoolScope(BaseModel):
    school_id: UUID
    organization_id: UUID
    cooperative_id: UUID | None = None
    status: EntityStatus = EntityStatus.PENDING_OWNER_DECISION


class SupplierScope(BaseModel):
    supplier_id: UUID
    organization_id: UUID
    status: EntityStatus = EntityStatus.PENDING_OWNER_DECISION


class DeviceScope(BaseModel):
    device_id: UUID
    organization_id: UUID
    school_id: UUID | None = None
    supplier_id: UUID | None = None
    status: EntityStatus = EntityStatus.PENDING_OWNER_DECISION


class RbacBinding(BaseModel):
    binding_id: UUID
    organization_id: UUID
    principal_id: UUID
    role: RbacRole
    scope_type: ScopeType
    scope_id: UUID
    granted_by: UUID
    active: bool = True


class AuthorizationRequest(BaseModel):
    principal_id: UUID
    organization_id: UUID
    permission: Permission
    scope_type: ScopeType
    scope_id: UUID


def is_allowed(request: AuthorizationRequest, bindings: list[RbacBinding]) -> bool:
    """Fail closed: require an active same-organization binding at exact scope."""
    return any(
        binding.active
        and binding.principal_id == request.principal_id
        and binding.organization_id == request.organization_id
        and binding.scope_type == request.scope_type
        and binding.scope_id == request.scope_id
        and request.permission in ROLE_PERMISSIONS[binding.role]
        for binding in bindings
    )
