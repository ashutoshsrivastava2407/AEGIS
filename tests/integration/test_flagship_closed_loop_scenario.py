"""AEGIS Flagship End-to-End Closed-Loop Integration Scenario.

Demonstrates complete operating loop:
Sense → Understand → Predict → Reason → Decide → Act → Observe → Feedback → Learn
"""

import pytest
from packages.security import UserContext
from services.command_center.command_service import EnterpriseCommandCenterService
from services.learning.learning_service import ContinuousLearningService
from services.operations.operations_service import ProductionOperationsPlatformService


def test_flagship_closed_loop_scenario():
    """Execute complete AEGIS enterprise intelligence & decision operating loop."""
    command_center = EnterpriseCommandCenterService()
    learning = ContinuousLearningService()
    operations = ProductionOperationsPlatformService()
    
    admin_user = UserContext(user_id="usr-flagship-admin", tenant_id="tenant-flagship", username="admin_flagship", email="admin@flagship.org", roles=["ENTERPRISE_ADMIN"])
    tenant_id = "tenant-flagship"

    # 1. SENSE: Record operational learning signal
    signal = learning.signals.record_signal(
        dimension="DATA",
        signal_type="HIGH_QUERY_LATENCY",
        source_component="QueryEngine",
        payload={"query_duration_ms": 350.0},
        tenant_id=tenant_id,
    )
    assert signal["signal_id"] is not None

    # 2. UNDERSTAND & PREDICT: Search global index & trace correlation
    search_res = command_center.search_engine.search(query="Revenue", user=admin_user)
    assert search_res["total_results"] >= 0

    trace_tree = command_center.trace_explorer.reconstruct_trace(tenant_id=tenant_id)
    assert trace_tree["causality_chain_intact"] is True

    # 3. REASON & DECIDE: Evaluate Step 10 policy governance
    policy_res = operations.remediation.policy_engine.evaluate_policy(
        subject_id=admin_user.user_id,
        resource_id="aegis-api",
        action="SCALE_SERVICE_WORKERS",
        context={"user_role": "ENTERPRISE_ADMIN", "risk_level": "MEDIUM"},
        tenant_id=tenant_id,
    )
    assert policy_res["decision"] == "ALLOW"

    # 4. ACT: Execute governed remediation
    rem_result = operations.remediation.execute_remediation(
        remediation_action="RESTART_POD",
        target_service_id="aegis-api",
        parameters={"risk_level": "MEDIUM"},
        actor_id=admin_user.user_id,
        tenant_id=tenant_id,
        user_role="ENTERPRISE_ADMIN",
    )
    assert rem_result["execution_status"] == "SUCCESS"
    assert rem_result["evidence_hash"] is not None

    # 5. OBSERVE & FEEDBACK: Compute DiD outcome attribution
    attribution = learning.attribution.attribute_outcome(
        action_id=rem_result["remediation_id"],
        treatment_pre_avg=120.0,
        treatment_post_avg=35.0,
        control_pre_avg=120.0,
        control_post_avg=115.0,
        sample_size=500,
        tenant_id=tenant_id,
    )
    assert attribution["methodology"] == "AEGIS_DiD_v1.0"
    assert attribution["is_statistically_significant"] is True

    # 6. LEARN: Propose and promote continuous learning improvement candidate
    candidate = learning.lifecycle.propose_candidate(
        title="Promote Auto-Scaling Worker Thresholds",
        target_subsystem="WORKFLOW",
        description="Auto-scale workers when latency exceeds 200ms.",
        proposal={"threshold_ms": 200},
        actor_id=admin_user.user_id,
        tenant_id=tenant_id,
    )
    promoted = learning.lifecycle.transition_candidate(
        candidate_id=candidate["candidate_id"],
        target_status="PROMOTED",
        actor_id=admin_user.user_id,
        tenant_id=tenant_id,
        user_role="ENTERPRISE_ADMIN",
    )
    assert promoted["status"] == "PROMOTED"

    # 7. COMMAND CENTER OVERVIEW & READINESS GATE
    overview = command_center.get_command_center_overview(admin_user)
    assert overview["status"] == "OPERATIONAL"

    readiness = command_center.readiness_gate.evaluate_system_readiness(tenant_id=tenant_id)
    assert readiness["is_production_ready"] is True
    assert readiness["dimensions_evaluated_count"] == 19
