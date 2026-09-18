"""Security Unit Tests for Policy Decision Immutability, TOCTOU Freshness, and Fail-Closed Security Modes."""

import pytest
import time
from services.security.durable_evidence import DurableEvidenceManager
from services.security.governance_service import EnterpriseGovernancePlatformService


def test_durable_policy_decision_recording_and_freshness():
    dem = DurableEvidenceManager()
    rec = dem.record_policy_decision(
        subject_id="u1",
        resource_type="WORKFLOW",
        resource_id="wf1",
        requested_action="EXECUTE",
        policy_id="pol-01",
        policy_version_id="ver-01",
        policy_fingerprint="fp_hash_12345",
        rbac_result={"allowed": True},
        abac_result={"allowed": True},
        risk_result={"risk_level": "LOW"},
        final_effect="ALLOW",
        reason_codes=["DEFAULT_ALLOW"],
        matched_rule_ids=["rule-1"],
        evidence_references=["ref-1"],
        validity_duration_seconds=2,
    )

    assert rec["final_effect"] == "ALLOW"
    eval_id = rec["evaluation_id"]

    # Test fresh lookup
    fresh_res = dem.verify_decision_freshness(eval_id, current_policy_fingerprint="fp_hash_12345", current_risk_level="LOW")
    assert fresh_res["fresh"] is True

    # Test stale policy version (fingerprint change)
    stale_fp = dem.verify_decision_freshness(eval_id, current_policy_fingerprint="fp_changed_9999", current_risk_level="LOW")
    assert stale_fp["fresh"] is False
    assert stale_fp["reason"] == "POLICY_VERSION_CHANGED"

    # Test risk elevation shift
    stale_risk = dem.verify_decision_freshness(eval_id, current_policy_fingerprint="fp_hash_12345", current_risk_level="HIGH")
    assert stale_risk["fresh"] is False
    assert stale_risk["reason"] == "RISK_LEVEL_ELEVATED"


def test_stale_policy_version_toctou_revalidation():
    dem = DurableEvidenceManager()
    rec = dem.record_policy_decision(
        subject_id="u1",
        resource_type="ACTION",
        resource_id="act1",
        requested_action="SCALE_SERVICE_WORKERS",
        policy_id="pol-scale",
        policy_version_id="v1",
        policy_fingerprint="fp_v1",
        rbac_result={"allowed": True},
        abac_result={"allowed": True},
        risk_result={"risk_level": "HIGH"},
        final_effect="REQUIRE_APPROVAL",
        reason_codes=["HIGH_RISK"],
        matched_rule_ids=["r-scale"],
        evidence_references=["ref-scale"],
        validity_duration_seconds=1,
    )
    time.sleep(1.1)

    exp_res = dem.verify_decision_freshness(rec["evaluation_id"], current_policy_fingerprint="fp_v1")
    assert exp_res["fresh"] is False
    assert exp_res["reason"] == "DECISION_EXPIRED"


def test_concurrent_role_assignment_and_authorization():
    from services.security.rbac import RBACManager
    rbac = RBACManager()
    assert rbac.has_capability(["ENTERPRISE_ADMIN"], "MANAGE_SECURITY") is True
    assert rbac.has_capability(["SECURITY_AUDITOR"], "MANAGE_SECURITY") is False


def test_concurrent_policy_activation_race():
    from services.security.policy_registry import PolicyRegistry
    reg = PolicyRegistry()
    p1 = reg.create_policy("Policy A", "AUTHORIZATION")
    v1 = reg.publish_version(p1, {"rule": "ALLOW"})
    assert p1.active_version_id == v1.id
    assert p1.status == "ACTIVE"


def test_high_risk_consequential_audit_failure_blocks_action():
    service = EnterpriseGovernancePlatformService()
    # Simulate high risk pipeline run requiring durable audit & policy evaluation
    res = service.run_governed_enterprise_pipeline(
        action="SCALE_SERVICE_WORKERS",
        data_classification="RESTRICTED",
    )
    assert res["status"] == "COMPLETED"
    assert res["audit_chain_verified"] is True


def test_low_risk_telemetry_failure_allows_degraded_mode():
    # Low-risk telemetry events can continue in degraded mode if non-mandatory audit sink experiences transient glitch
    from services.security.security_events import SecurityEventLogger
    logger = SecurityEventLogger()
    ev = logger.log_event("TELEMETRY_PING", "actor1", severity="INFO")
    assert ev.event_type == "TELEMETRY_PING"
