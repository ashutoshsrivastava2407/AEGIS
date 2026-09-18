"""Test suite for DiD Outcome Attribution & Executive Intelligence Reports."""

import pytest
from services.learning.attribution import OutcomeAttributionEngine
from services.learning.executive import ExecutiveIntelligenceAndScenarioEngine


def test_outcome_attribution_did_methodology():
    attr = OutcomeAttributionEngine()
    
    # Valid Difference-in-Differences calculation
    obs = attr.attribute_outcome(
        action_id="act-scale-workers",
        treatment_pre_avg=100.0,
        treatment_post_avg=75.0,  # 25 ms reduction
        control_pre_avg=100.0,
        control_post_avg=95.0,    # 5 ms reduction
        sample_size=1000,
    )
    assert obs["methodology"] == "AEGIS_DiD_v1.0"
    assert obs["did_estimate"] == -20.0  # (-25) - (-5) = -20 ms net improvement
    assert obs["is_statistically_significant"] is True

    # Insufficient sample size -> returns ATTRIBUTION_UNAVAILABLE
    unavail = attr.attribute_outcome(
        action_id="act-small-sample",
        treatment_pre_avg=100.0,
        treatment_post_avg=80.0,
        control_pre_avg=100.0,
        control_post_avg=95.0,
        sample_size=15,  # < 30
    )
    assert unavail["status"] == "ATTRIBUTION_UNAVAILABLE"


def test_executive_reports_and_scenario_simulations():
    exec_engine = ExecutiveIntelligenceAndScenarioEngine()
    
    report = exec_engine.generate_executive_report(title="Q4 Platform Governance Report")
    assert report["title"] == "Q4 Platform Governance Report"
    assert len(report["observed_facts"]) >= 1
    assert len(report["model_predictions"]) >= 1
    assert len(report["system_recommendations"]) >= 1
    assert len(report["decisions_executed"]) >= 1
    assert len(report["attributions"]) >= 1

    scenario = exec_engine.create_scenario_analysis()
    assert scenario["title"] == "Multi-Region Cloud Capacity Scaling Scenario"
    assert "baseline_scenario" in scenario
    assert len(scenario["alternative_scenarios"]) >= 2
    assert scenario["recommended_option_id"] == "opt-multi-region"
