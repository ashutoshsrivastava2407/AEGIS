"""Security Test Suite for Cross-Tenant Isolation, ABAC Context, Data Masking, Break-Glass, and Tamper Evidence."""

import pytest
from services.security.authorization import AuthorizationEngine
from services.security.abac import ABACEvaluator
from services.security.data_governance import DataGovernanceEngine
from services.security.privileged_access import BreakGlassManager
from services.security.audit_integrity import TamperEvidentAuditTrail


def test_cross_tenant_access_isolation_blocking():
    abac = ABACEvaluator()
    res = abac.evaluate_attributes(
        subject_attrs={"tenant_id": "tenant-A", "business_domain": "FINANCE"},
        resource_attrs={"tenant_id": "tenant-B", "business_domain": "FINANCE"},
        environment_attrs={"auth_strength": "NORMAL_AUTH"},
    )
    assert res["allowed"] is False
    assert any("Cross-tenant" in r for r in res["reasons"])


def test_restricted_data_auth_strength_gating():
    abac = ABACEvaluator()
    res = abac.evaluate_attributes(
        subject_attrs={"tenant_id": "default", "business_domain": "ENTERPRISE"},
        resource_attrs={"tenant_id": "default", "classification": "RESTRICTED"},
        environment_attrs={"auth_strength": "NORMAL_AUTH"},
    )
    assert res["allowed"] is False
    assert any("RESTRICTED" in r for r in res["reasons"])


def test_field_level_sensitive_data_masking():
    dge = DataGovernanceEngine()
    data = {"ssn": "123-45-6789", "salary": 150000, "description": "User email test@aegis.com info"}
    masked = dge.mask_sensitive_payload(data, user_role="ANALYST")
    assert masked["ssn"] == "***MASKED***"
    assert masked["salary"] == "***MASKED***"
    assert "[REDACTED_PII]" in masked["description"]


def test_break_glass_session_expiration():
    bgm = BreakGlassManager()
    session = bgm.activate_break_glass("admin1", "Emergency testing", duration_minutes=-1)
    assert bgm.validate_session(session) is False
    assert session.status == "EXPIRED"


def test_tamper_evident_audit_chain_tamper_detection():
    trail = TamperEvidentAuditTrail()
    events = [
        {"id": "ev1", "actor_id": "u1", "action": "LOGIN", "details": {"ip": "1.1.1.1"}},
        {"id": "ev2", "actor_id": "u1", "action": "EXECUTE", "details": {"target": "wf1"}},
    ]
    chain = trail.build_audit_chain(events)

    # Tamper with an event in the chain
    chain[1]["action"] = "UNAUTHORIZED_TAMPER"
    verification = trail.verify_chain_integrity(chain)
    assert verification["valid"] is False
    assert verification["tampered_events_count"] == 1
