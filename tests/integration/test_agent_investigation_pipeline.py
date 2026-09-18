"""AEGIS Autonomous Agent Platform End-to-End Integration Test."""

import pytest
from services.agents.services import agent_platform_service


def test_end_to_end_revenue_anomaly_investigation_pipeline():
    """Verify flagship end-to-end multi-agent investigation workflow."""

    goal = "Investigate root cause of Q3 regional revenue drop anomaly"
    
    result = agent_platform_service.execute_agent_run(
        goal=goal,
        agent_type="SUPERVISOR",
        tenant_id="tenant-aegis-primary"
    )

    assert result["run_id"] is not None
    assert result["status"] == "COMPLETED"
    assert result["plan_id"] is not None
    assert result["total_steps"] >= 4
    assert len(result["executed_nodes"]) >= 4

    # Verify Verification Agent findings
    ver = result["verification"]
    assert ver is not None
    assert ver["is_verified"] is True
    assert ver["groundedness_score"] >= 0.70

    # Verify Quantitative Evaluation
    ev = result["evaluation"]
    assert ev is not None
    assert ev["goal_completion_score"] == 1.0
    assert ev["total_cost_usd"] > 0.0
