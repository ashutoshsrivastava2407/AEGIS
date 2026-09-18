"""Test suite for Learning Signals & Governed Improvement Candidate Lifecycle."""

import pytest
from services.learning.signals import LearningSignalEngine
from services.learning.lifecycle import GovernedImprovementLifecycleEngine


def test_learning_signal_recording_and_querying():
    engine = LearningSignalEngine()
    
    sig1 = engine.record_signal(
        dimension="ML",
        signal_type="PSI_DRIFT_EXCEEDED",
        source_component="PSI_Detector",
        payload={"psi": 0.28, "model": "demand_forecaster"},
        severity="HIGH",
    )
    assert sig1["dimension"] == "ML"
    assert sig1["severity"] == "HIGH"

    signals = engine.list_signals(dimension="ML")
    assert len(signals) >= 1
    assert signals[0]["signal_id"] == sig1["signal_id"]


def test_governed_improvement_candidate_lifecycle():
    lifecycle = GovernedImprovementLifecycleEngine()
    
    cand = lifecycle.propose_candidate(
        title="Retrain Demand Forecaster ML Model",
        target_subsystem="ML",
        description="Retrain model on recent 90d Gold transactions dataset.",
        proposal={"dataset_id": "ds_rev_01"},
    )
    assert cand["status"] == "OBSERVED"

    # Transition through stages
    c1 = lifecycle.transition_candidate(cand["id"], "EVALUATING")
    assert c1["status"] == "EVALUATING"

    c2 = lifecycle.transition_candidate(cand["id"], "APPROVED", user_role="ENTERPRISE_ADMIN")
    assert c2["status"] == "APPROVED"
    assert c2["policy_evaluation_id"] is not None

    c3 = lifecycle.transition_candidate(cand["id"], "PROMOTED", user_role="ENTERPRISE_ADMIN")
    assert c3["status"] == "PROMOTED"
    assert c3["promoted_at"] is not None

    # Non-admin user promotion blocked by Step 10 policy
    c_blocked = lifecycle.transition_candidate(cand["id"], "PROMOTED", user_role="READONLY_USER")
    assert c_blocked["status"] == "BLOCKED_BY_POLICY"
