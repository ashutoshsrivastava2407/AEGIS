"""Unit Test Suite for AEGIS Decision Platform Engine."""

import pytest
from services.decisions.contracts import ActionContractRegistry, ActionContract
from services.decisions.registry import DecisionRegistry
from services.decisions.context import DecisionContextBuilder
from services.decisions.gates import DecisionIntegrityEvaluator, DecisionEligibilityEvaluator
from services.decisions.evidence import EvidenceManager
from services.decisions.options import MultiOptionGenerator
from services.decisions.evaluation import MCDAEvaluator
from services.decisions.optimization import OptimizationEngine
from services.decisions.risk import QuantitativeRiskEngine
from services.decisions.uncertainty import UncertaintyEngine
from services.decisions.simulation import SimulationEngine
from services.decisions.policy import ServerDecisionPolicyEngine
from services.decisions.approvals import DecisionApprovalEngine
from services.decisions.outcomes import OutcomeTracker
from services.decisions.feedback import FeedbackEngine
from services.decisions.verification import DecisionVerificationGate
from packages.database.models.decision import DecisionModel


def test_action_contract_registry():
    """Verify ActionContractRegistry validation and contract retrieval."""
    registry = ActionContractRegistry()
    contract = registry.get_contract("SCALE_SERVICE_WORKERS", "1.0.0")
    assert contract is not None
    assert contract.action_type == "SCALE_SERVICE_WORKERS"

    validation = registry.validate_action("SCALE_SERVICE_WORKERS", {"service_name": "analytics-worker", "target_replicas": 4})
    assert validation["valid"] is True

    validation_missing = registry.validate_action("SCALE_SERVICE_WORKERS", {})
    assert validation_missing["valid"] is False


def test_optimistic_concurrency_registry():
    """Verify state machine transitions and optimistic concurrency version locking."""
    reg = DecisionRegistry()
    decision = DecisionModel(
        id="dec-100",
        tenant_id="default",
        owner="admin",
        requester="admin",
        objective="Test objective",
        decision_type="RESOURCE_ALLOCATION",
        decision_status="CREATED",
        version=1
    )

    # Valid transition with matching version
    res = reg.update_decision_state(decision, "CONTEXT_BUILDING", expected_version=1)
    assert res["success"] is True
    assert decision.decision_status == "CONTEXT_BUILDING"
    assert decision.version == 2

    # Stale transition attempt (expected version 1, but current version is 2)
    stale_res = reg.update_decision_state(decision, "EVALUATING", expected_version=1)
    assert stale_res["success"] is False
    assert stale_res["stale"] is True
    assert decision.decision_status == "CONTEXT_BUILDING"


def test_canonical_context_fingerprint():
    """Verify canonical JSON serialization and SHA-256 fingerprint reproducibility."""
    builder = DecisionContextBuilder()
    data1 = {"b": 2, "a": 1, "nested": {"y": 20, "x": 10}}
    data2 = {"a": 1, "b": 2, "nested": {"x": 10, "y": 20}}

    hash1 = builder.generate_context_fingerprint(data1)
    hash2 = builder.generate_context_fingerprint(data2)

    assert hash1 == hash2
    assert len(hash1) == 64


def test_pre_approval_staleness_detection():
    """Verify detection of context staleness before approval."""
    snapshot = {"policies": [{"version": "1.0.0"}]}
    staleness = DecisionContextBuilder.detect_context_staleness(
        snapshot=snapshot,
        current_data_freshness_seconds=5000.0,  # exceeds 3600s
        current_model_drift_score=0.10,
        current_policy_version="1.0.0"
    )
    assert staleness["is_stale"] is True
    assert staleness["code"] == "STALE_CONTEXT"


def test_integrity_and_eligibility_gates():
    """Verify machine evaluation of integrity and eligibility dual states."""
    integrity = DecisionIntegrityEvaluator.evaluate(
        data_quality_score=0.98,
        data_freshness_seconds=120.0,
        model_health_score=0.95,
        evidence_conflict_detected=False
    )
    assert integrity["status"] == "VALID"

    eligibility = DecisionEligibilityEvaluator.evaluate(
        integrity_status="VALID",
        risk_tier="LOW_RISK",
        approval_status="APPROVED"
    )
    assert eligibility["status"] == "AUTO_EXECUTION_ELIGIBLE"


def test_evidence_manager_conflict_detection():
    """Verify evidence processing and directional conflict detection."""
    manager = EvidenceManager()
    evidences = [
        {"title": "Report A", "source_type": "OBSERVED", "source_ref": "ref-1", "evidence_summary": "Revenue will increase significantly"},
        {"title": "Report B", "source_type": "DOCUMENT", "source_ref": "ref-2", "evidence_summary": "Revenue will decrease dramatically"}
    ]
    result = manager.process_evidence_set(evidences)
    assert result["has_conflicts"] is True
    assert result["conflict_count"] == 1


def test_unit_aware_mcda_evaluation():
    """Verify MCDA scoring, Expected Value, Net Value, RAV, and Pareto dominance."""
    evaluator = MCDAEvaluator()
    generator = MultiOptionGenerator()
    options = generator.generate_options("RESOURCE_ALLOCATION", "Test Objective", [])
    criteria = [
        {"criterion_key": "EXPECTED_BENEFIT", "name": "Benefit", "weight": 0.5, "unit": "USD"},
        {"criterion_key": "COST", "name": "Cost", "weight": 0.3, "unit": "USD"},
        {"criterion_key": "RISK", "name": "Risk", "weight": 0.2, "unit": "SCALAR"}
    ]
    results = evaluator.evaluate_options(options, criteria)
    assert len(results) == len(options)
    for r in results:
        assert "mcda_score" in r
        assert "expected_value" in r
        assert "risk_adjusted_value" in r
        assert "is_pareto_efficient" in r


def test_pluggable_optimization_engine():
    """Verify constrained optimization solution."""
    opt_engine = OptimizationEngine()
    vars_list = [
        {"name": "worker_scale", "cost": 1200.0, "expected_return": 15000.0, "max_allocation": 4}
    ]
    constraints = [{"constraint_key": "MAX_BUDGET", "threshold_value": 5000.0, "operator": "<="}]
    res = opt_engine.optimize("RESOURCE_ALLOCATION", "MAXIMIZE_REVENUE", vars_list, constraints, budget_limit=5000.0)
    assert res["status"] in ("HEURISTIC_NEAR_OPTIMAL", "FEASIBLE")
    assert res["objective_value"] == 15000.0


def test_quantitative_risk_engine():
    """Verify risk calculation, expected loss, blast radius, and reversibility."""
    risk_eng = QuantitativeRiskEngine()
    assessment = risk_eng.assess_risk(probability=0.20, impact_usd=10000.0, affected_services_count=1)
    assert assessment["expected_loss_usd"] == 2000.0
    assert assessment["blast_radius"] == "LOCALIZED"
    assert assessment["reversibility"] == "REVERSIBLE"


def test_model_uncertainty_adapter_fallback():
    """Verify uncertainty adapter reporting when uncertainty capability is absent."""
    unc_eng = UncertaintyEngine()
    res = unc_eng.calculate_uncertainty("no_uncertainty_model", [0.5], {"supports_uncertainty": False})
    assert res["uncertainty_type"] == "UNCERTAINTY_UNAVAILABLE"
    assert res["is_available"] is False


def test_simulation_stochastic_basis_guard():
    """Verify simulation engine falls back to deterministic analysis when stochastic basis is absent."""
    sim_eng = SimulationEngine()
    res = sim_eng.run_simulation(base_value=10000.0, stochastic_basis={"has_valid_distribution": False}, seed=42)
    assert res["simulation_type"] == "DETERMINISTIC"
    assert res["has_valid_stochastic_basis"] is False

    # Run Monte Carlo when stochastic basis exists
    res_mc = sim_eng.run_simulation(base_value=10000.0, stochastic_basis={"has_valid_distribution": True}, seed=42)
    assert res_mc["simulation_type"] == "MONTE_CARLO"
    assert res_mc["iterations"] == 1000


def test_toctou_pre_execution_revalidation():
    """Verify TOCTOU approval revalidation fails when context fingerprint changes."""
    app_engine = DecisionApprovalEngine()
    approval = app_engine.process_approval_action("dec-1", "user-1", "APPROVER", "APPROVE")
    
    # Matching fingerprint -> Valid
    reval_valid = app_engine.revalidate_approval_before_execution(approval, "hash-A", "hash-A")
    assert reval_valid["is_valid"] is True
    assert reval_valid["status"] == "APPROVED"

    # Mismatched fingerprint -> Invalidated
    reval_invalid = app_engine.revalidate_approval_before_execution(approval, "hash-A", "hash-B")
    assert reval_invalid["is_valid"] is False
    assert reval_invalid["status"] == "APPROVAL_INVALIDATED"


def test_feedback_calibration_proposal_and_rollback():
    """Verify controlled calibration proposal creation, approval, and versioned rollback."""
    fb_engine = FeedbackEngine()
    prop = fb_engine.create_calibration_proposal(
        decision_id="dec-1",
        outcome_id="out-1",
        target_component="CRITERIA_WEIGHT",
        previous_config={"version": 1, "weight": 0.5, "version_string": "1.0.0"},
        observed_variance_usd=1200.0
    )
    assert prop["governance_status"] == "PROPOSED"
    assert prop["proposal_version"] == "v2.0.0"

    # Rollout
    rolled_out = fb_engine.approve_and_rollout_calibration(prop, "admin")
    assert rolled_out["is_rolled_out"] is True

    # Rollback
    rollback_res = fb_engine.rollback_calibration(rolled_out, "Regression detected in monitoring")
    assert rollback_res["status"] == "ROLLED_BACK"
    assert rollback_res["restored_version"] == "1.0.0"
