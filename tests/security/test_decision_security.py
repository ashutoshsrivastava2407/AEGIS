"""Security Test Suite for AEGIS Decision Platform."""

import pytest
from services.decisions.services import DecisionPlatformService
from services.decisions.policy import ServerDecisionPolicyEngine
from services.decisions.approvals import DecisionApprovalEngine
from packages.database.models.agent_execution import AgentStepModel


def test_cross_tenant_decision_isolation():
    """Verify tenant isolation in policy engine."""
    policy_engine = ServerDecisionPolicyEngine()
    
    # Valid tenant
    res_valid = policy_engine.evaluate_policy("tenant-A", "user", "ALLOCATION", 1000.0, "LOW_RISK", [])
    assert res_valid["policy_result"] != "DENY"

    # Invalid / Missing tenant -> DENY
    res_invalid = policy_engine.evaluate_policy("", "user", "ALLOCATION", 1000.0, "LOW_RISK", [])
    assert res_invalid["policy_result"] == "DENY"


def test_high_risk_rejection_blocks_execution():
    """Verify high-risk action rejected at approval gate is blocked from execution."""
    approval_engine = DecisionApprovalEngine()
    rejection = approval_engine.process_approval_action(
        decision_id="dec-risk-1",
        approver_id="security-officer",
        approver_role="DECISION_APPROVER",
        action="REJECT",
        rationale="Rejected due to high operational exposure."
    )
    assert rejection["approval_status"] == "REJECTED"

    reval = approval_engine.revalidate_approval_before_execution(rejection, "hash-1", "hash-1")
    assert reval["is_valid"] is False
    assert reval["status"] == "APPROVAL_INVALIDATED"


def test_stale_approval_toctou_invalidation():
    """Verify context modification after approval invalidates approval upon execution attempt."""
    approval_engine = DecisionApprovalEngine()
    approval = approval_engine.process_approval_action("dec-toctou-1", "admin", "APPROVER", "APPROVE")
    
    # Context modified after approval signoff
    reval = approval_engine.revalidate_approval_before_execution(approval, "original-hash-123", "modified-hash-456")
    assert reval["is_valid"] is False
    assert reval["status"] == "APPROVAL_INVALIDATED"
    assert "Context fingerprint mismatch" in reval["reason"]


def test_client_field_override_rejection():
    """Verify policy engine server-side evaluation ignores client-supplied override attempts."""
    policy_engine = ServerDecisionPolicyEngine()
    # Client sends low risk, but high cost ($100,000)
    res = policy_engine.evaluate_policy("tenant-1", "user", "ALLOCATION", 100000.0, "LOW_RISK", [])
    assert res["policy_result"] == "REQUIRE_ESCALATION"
    assert "FINANCIAL_EXPOSURE_EXCEEDS_50K" in res["matched_rules"]


def test_storage_level_chain_of_thought_remediation():
    """Verify AgentStepModel no longer exposes raw thought_process attribute."""
    step = AgentStepModel(
        run_id="run-1",
        step_number=1,
        agent_type="ResearchAgent",
        action_type="THINK",
        rationale_summary="Analyzed revenue metrics and verified baseline."
    )
    assert hasattr(step, "rationale_summary")
    assert step.rationale_summary == "Analyzed revenue metrics and verified baseline."
    assert not hasattr(step, "thought_process")
