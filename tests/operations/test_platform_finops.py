"""Test suite for Platform FinOps Cost Attribution & Anomaly Detection."""

import pytest
from services.operations.finops import PlatformFinOpsService


def test_cost_event_recording_and_attribution():
    finops = PlatformFinOpsService()
    
    evt = finops.record_cost_event(
        service_id="llm-inference",
        workload_id="rag-query-worker",
        domain="LLM_TOKENS",
        api_tokens=50000,
        cost_usd=0.25,
    )
    assert evt["domain"] == "LLM_TOKENS"
    assert evt["cost_usd"] == 0.25

    summary = finops.get_cost_summary()
    assert summary["total_cost_usd"] >= 0.25
    assert "LLM_TOKENS" in summary["cost_by_domain"]


def test_budget_creation_and_anomaly_detection():
    finops = PlatformFinOpsService()
    
    bgt = finops.create_budget(
        service_id="analytics-engine",
        budget_usd=100.0,
        notify_threshold_pct=80.0,
    )
    assert bgt["budget_usd"] == 100.0

    # Inject 10x cost spike to trigger anomaly detection
    finops.record_cost_event(
        service_id="analytics-engine",
        workload_id="heavy-etl",
        domain="COMPUTE",
        cost_usd=1.50,  # > 5x baseline (0.05)
    )

    anomalies = finops.list_anomalies()
    assert len(anomalies) >= 1
    assert anomalies[0]["service_id"] == "analytics-engine"
    assert anomalies[0]["anomaly_score"] >= 5.0
