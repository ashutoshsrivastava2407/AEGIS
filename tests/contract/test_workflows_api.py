"""AEGIS Action & Workflow Automation Platform REST API Contract Tests."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_workflows_list_api_contract():
    """Verify GET /api/v1/workflows contract."""
    res = client.get("/api/v1/workflows")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "data" in json_data


def test_create_workflow_api_contract():
    """Verify POST /api/v1/workflows contract."""
    res = client.post("/api/v1/workflows", json={
        "name": "API Contract Test Workflow",
        "description": "Created via API contract test",
        "business_domain": "INFRASTRUCTURE",
    })
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["name"] == "API Contract Test Workflow"


def test_trigger_closed_loop_api_contract():
    """Verify POST /api/v1/workflows/runs/closed-loop contract."""
    res = client.post("/api/v1/workflows/runs/closed-loop", json={
        "name": "Automated Infrastructure Closed Loop",
        "business_domain": "INFRASTRUCTURE",
        "trigger_payload": {"cpu": 88.5}
    })
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["completed_stages"] == 16
    assert json_data["data"]["operating_loop"] == "16-STAGE_CANONICAL_CLOSED_LOOP"
    assert json_data["data"]["did_estimation_model"] == "AEGIS_DiD_v1.0"


def test_workflows_observability_metrics_api_contract():
    """Verify GET /api/v1/workflows/observability/metrics contract."""
    res = client.get("/api/v1/workflows/observability/metrics")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "total_runs" in json_data["data"]
