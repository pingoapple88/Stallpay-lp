from uuid import uuid4

from app.scope_rbac import (
    AuthorizationRequest,
    Permission,
    RbacBinding,
    RbacRole,
    ScopeType,
    is_allowed,
)


def test_school_coordinator_can_read_orders_at_exact_school_scope() -> None:
    organization_id = uuid4()
    school_id = uuid4()
    principal_id = uuid4()
    binding = RbacBinding(
        binding_id=uuid4(),
        organization_id=organization_id,
        principal_id=principal_id,
        role=RbacRole.SCHOOL_COORDINATOR,
        scope_type=ScopeType.SCHOOL,
        scope_id=school_id,
        granted_by=uuid4(),
    )
    request = AuthorizationRequest(
        principal_id=principal_id,
        organization_id=organization_id,
        permission=Permission.ORDER_READ,
        scope_type=ScopeType.SCHOOL,
        scope_id=school_id,
    )
    assert is_allowed(request, [binding]) is True


def test_supplier_cannot_operate_device_or_cross_organization_scope() -> None:
    organization_id = uuid4()
    supplier_id = uuid4()
    device_id = uuid4()
    principal_id = uuid4()
    binding = RbacBinding(
        binding_id=uuid4(),
        organization_id=organization_id,
        principal_id=principal_id,
        role=RbacRole.SUPPLIER_OPERATOR,
        scope_type=ScopeType.SUPPLIER,
        scope_id=supplier_id,
        granted_by=uuid4(),
    )
    device_request = AuthorizationRequest(
        principal_id=principal_id,
        organization_id=organization_id,
        permission=Permission.DEVICE_OPERATE,
        scope_type=ScopeType.DEVICE,
        scope_id=device_id,
    )
    cross_org_request = device_request.model_copy(update={"organization_id": uuid4()})
    assert is_allowed(device_request, [binding]) is False
    assert is_allowed(cross_org_request, [binding]) is False


def test_inactive_binding_fails_closed() -> None:
    binding = RbacBinding(
        binding_id=uuid4(),
        organization_id=uuid4(),
        principal_id=uuid4(),
        role=RbacRole.ORGANIZATION_ADMIN,
        scope_type=ScopeType.ORGANIZATION,
        scope_id=uuid4(),
        granted_by=uuid4(),
        active=False,
    )
    request = AuthorizationRequest(
        principal_id=binding.principal_id,
        organization_id=binding.organization_id,
        permission=Permission.RBAC_MANAGE,
        scope_type=ScopeType.ORGANIZATION,
        scope_id=binding.scope_id,
    )
    assert is_allowed(request, [binding]) is False
