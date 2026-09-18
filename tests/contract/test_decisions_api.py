"""AEGIS Decision Platform REST API Contract Tests."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_decisions_list_api_contract():
    """Verify GET /api/v1/decisions contract."""
    res = client.get("/api/v1/decisions")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "data" in json_data


def test_create_decision_pipeline_api_contract():
    """Verify POST /api/v1/decisions contract."""
    res = client.post("/api/v1/decisions", json={
        "objective": "API Contract Test Objective",
        "decision_type": "RESOURCE_ALLOCATION",
        "seed": 42
    })
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["stages_completed"] == 14


def test_simulation_api_contract():
    """Verify POST /api/v1/decisions/simulation contract."""
    res = client.post("/api/v1/decisions/simulation", json={
        "base_value": 10000.0,
        "iterations": 500,
        "seed": 42,
        "stochastic_basis": {"has_valid_distribution": True}
    })
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["simulation_type"] == "MONTE_CARLO"
    assert json_data["data"]["iterations"] == 500


def test_decision_approval_api_contract():
    """Verify POST /api/v1/decisions/{decision_id}/approve contract."""
    res = client.post("/api/v1/decisions/dec-test-1/approve", json={
        "action": "APPROVE",
        "rationale": "Approved via contract test"
    })
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["approval_status"] == "APPROVED"


def test_decision_execute_action_api_contract():
    """Verify POST /api/v1/decisions/{decision_id}/execute contract."""
    res = client.post("/api/v1/decisions/dec-test-1/execute", json={
        "action_type": "SCALE_SERVICE_WORKERS",
        "target_resource": "service:analytics-worker",
        "parameters": {"service_name": "analytics-worker", "target_replicas": 4},
        "idempotency_key": "contract-key-123"
    })
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["execution_status"] == "EXECUTED"


def test_decision_feedback_api_contract():
    """Verify POST /api/v1/decisions/{decision_id}/feedback contract."""
    res = client.post("/api/v1/decisions/dec-test-1/feedback", json={
        "outcome_id": "out-1",
        "target_component": "CRITERIA_WEIGHT",
        "previous_config": {"version": 1, "weight": 0.5, "version_string": "1.0.0"},
        "observed_variance_usd": 1200.0
    })
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["governance_status"] == "PROPOSED"
