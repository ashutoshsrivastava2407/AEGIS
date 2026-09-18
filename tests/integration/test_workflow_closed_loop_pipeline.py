"""Integration Test for Canonical 16-Stage Closed-Loop Operating Loop Pipeline."""

import pytest
from services.workflows.services import WorkflowPlatformService


def test_16_stage_closed_loop_execution_pipeline():
    service = WorkflowPlatformService()
    result = service.execute_closed_loop_workflow(
        name="16-Stage Closed Loop Integration Test",
        owner="integration-tester@aegis.enterprise",
        business_domain="INFRASTRUCTURE",
        tenant_id="default",
        trigger_payload={"cpu_utilization": 92.4, "latency_ms": 450, "region": "us-east-1"},
    )

    assert result["status"] == "COMPLETED"
    assert result["operating_loop"] == "16-STAGE_CANONICAL_CLOSED_LOOP"
    assert result["total_stages"] == 16
    assert result["completed_stages"] == 16
    assert result["did_estimation_model"] == "AEGIS_DiD_v1.0"

    trace = result["stage_trace"]
    assert len(trace) == 16

    stage_names = [st["stage_name"] for st in trace]
    expected_stages = [
        "Signal",
        "Context",
        "Investigation",
        "Evidence",
        "Options",
        "Evaluation",
        "Simulation",
        "Risk & Uncertainty",
        "Policy",
        "Decision",
        "Approval",
        "Orchestrate",
        "Act",
        "Verify",
        "Outcome",
        "Feedback & Learning",
    ]
    assert stage_names == expected_stages

    # Verify Stage 16 Feedback & Learning DID metrics
    feedback_stage = trace[15]
    assert feedback_stage["stage_name"] == "Feedback & Learning"
    assert feedback_stage["output"]["did_model"] == "AEGIS_DiD_v1.0"
    assert feedback_stage["output"]["causal_effect_estimate"] == -180.0
    assert feedback_stage["output"]["model_fine_tuning_enqueued"] is True
