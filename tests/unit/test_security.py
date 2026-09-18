"""Unit Tests for AEGIS Security & Tenant Isolation."""

from packages.security import (
    UserContext,
    create_access_token,
    decode_access_token,
    security_evaluator,
    Permission,
)


def test_jwt_encode_decode():
    user = UserContext(
        user_id="usr_123",
        tenant_id="tnt_789",
        username="alice",
        email="alice@aegis.enterprise",
        roles=["ANALYST"],
        permissions=[Permission.DATA_READ],
    )

    token = create_access_token(user)
    assert token is not None

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.user_id == "usr_123"
    assert decoded.tenant_id == "tnt_789"
    assert Permission.DATA_READ in decoded.permissions


def test_security_evaluator_permissions():
    user = UserContext(
        user_id="usr_123",
        tenant_id="tnt_789",
        username="alice",
        email="alice@aegis.enterprise",
        permissions=[Permission.DATA_READ],
        is_admin=False,
    )

    assert security_evaluator.evaluate_permission(user, Permission.DATA_READ) is True
    assert security_evaluator.evaluate_permission(user, Permission.SYSTEM_ADMIN) is False


def test_tenant_boundary_isolation():
    user = UserContext(
        user_id="usr_123",
        tenant_id="tenant_a",
        username="alice",
        email="alice@aegis.enterprise",
    )

    assert security_evaluator.evaluate_tenant_boundary(user, "tenant_a") is True
    assert security_evaluator.evaluate_tenant_boundary(user, "tenant_b") is False
