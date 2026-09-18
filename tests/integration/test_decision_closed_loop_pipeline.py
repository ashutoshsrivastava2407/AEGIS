"""Flagship End-to-End 14-Stage Closed-Loop Integration Test."""

import pytest
from services.decisions.services import DecisionPlatformService


def test_end_to_end_14_stage_closed_loop_decision_pipeline():
    """Execute complete 14-stage decision loop for Q3 Regional Revenue Anomaly."""
    service = DecisionPlatformService()

    result = service.run_full_decision_pipeline(
        tenant_id="default",
        owner="revenue-director@aegis.enterprise",
        requester="agent:master-supervisor",
        objective="Q3 Regional Revenue Anomaly Mitigation & Analytics Compute Optimization",
        decision_type="RESOURCE_ALLOCATION",
        business_domain="FINANCE",
        user_role="ENTERPRISE_ADMIN",
        seed=42
    )

    # Assert 14 stages completed
    assert result["stages_completed"] == 14
    assert result["decision_id"] is not None
    assert result["decision_version_id"] is not None
    assert result["signal_id"] is not None
    assert result["context_id"] is not None
    assert result["investigation_run_id"] is not None
    assert isinstance(result["evidence_ids"], list)
    assert isinstance(result["option_ids"], list)
    assert result["evaluation_id"] is not None
    assert result["simulation_id"] is not None
    assert result["risk_id"] is not None
    assert result["uncertainty_id"] is not None
    assert result["policy_evaluation_id"] is not None
    assert result["approval_id"] is not None
    assert result["action_id"] is not None
    assert result["outcome_id"] is not None
    assert result["feedback_id"] is not None
    assert result["trace_id"] is not None
    assert result["manifest_id"] is not None
    assert len(result["manifest_hash"]) == 64
    assert result["tenant_id"] == "default"
    assert result["status"] == "CLOSED"

    # Stage 2: Context Snapshot & SHA-256 Fingerprint
    assert result["context_fingerprint"] is not None
    assert len(result["context_fingerprint"]) == 64

    # Stage 9: Integrity & Eligibility Dual States
    assert result["integrity_status"] == "VALID"
    assert result["eligibility_status"] in ("AUTO_EXECUTION_ELIGIBLE", "APPROVAL_REQUIRED")

    # Stage 10: Decision Verification
    assert result["verification_status"] == "VERIFIED"

    # Stage 11: TOCTOU Revalidation
    assert result["toctou_revalidation"]["is_valid"] is True

    # Stage 12: Action Execution Integrity & Outbox Event Dispatch (Action Semantic Integrity Verification)
    assert result["action_execution"]["success"] is True
    assert result["action_execution"]["execution_status"] == "EXECUTED"
    assert result["action_execution"]["tool_name"] == "scale_service_workers"
    assert result["action_execution"]["postconditions_verified"] is True
    assert "outbox_event" in result["action_execution"]

    # Stage 13: Outcome Measurement & Attribution Discipline (Causal Verification)
    assert result["outcome"]["attribution_classification"] == "CAUSALLY_ESTIMATED"
    assert result["outcome"]["causal_methodology_version"] == "AEGIS_DiD_v1.0"
    assert result["outcome"]["counterfactual_baseline_usd"] == 14000.0
    assert len(result["outcome"]["identification_assumptions"]) >= 1
    assert result["outcome"]["actual_impact_usd"] == 16200.0

    # Stage 14: Controlled Calibration Proposal & Governance
    assert result["calibration_proposal"]["governance_status"] == "PROPOSED"
    assert result["calibration_proposal"]["proposal_version"] == "v2.0.0"

    # Dossier Generation & Manifest Verification
    dossier = result["dossier"]
    assert dossier["canonical_hash_verified"] is True
    assert dossier["manifest"]["manifest_version"] == "1.0.0"
    assert dossier["manifest"]["manifest_hash"] == result["manifest_hash"]
