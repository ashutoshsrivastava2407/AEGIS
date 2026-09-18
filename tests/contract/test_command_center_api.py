"""AEGIS Enterprise Command Center REST API Contract Tests."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_command_center_overview_api_contract():
    """Verify GET /api/v1/command-center/overview contract."""
    res = client.get("/api/v1/command-center/overview")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "OPERATIONAL"
    assert "enterprise_health" in json_data["data"]


def test_command_center_readiness_api_contract():
    """Verify GET /api/v1/command-center/readiness contract."""
    res = client.get("/api/v1/command-center/readiness")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["overall_status"] == "READY_FOR_PRODUCTION"


def test_command_center_trace_api_contract():
    """Verify GET /api/v1/command-center/trace contract."""
    res = client.get("/api/v1/command-center/trace")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "nodes" in json_data["data"]


def test_global_search_api_contract():
    """Verify GET /api/v1/search contract."""
    res = client.get("/api/v1/search?q=revenue")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "results" in json_data["data"]


def test_learning_signals_api_contract():
    """Verify GET /api/v1/learning/signals contract."""
    res = client.get("/api/v1/learning/signals")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True


def test_executive_reports_api_contract():
    """Verify GET /api/v1/executive/reports contract."""
    res = client.get("/api/v1/executive/reports")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "observed_facts" in json_data["data"]


def test_scenarios_api_contract():
    """Verify GET /api/v1/scenarios contract."""
    res = client.get("/api/v1/scenarios")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "baseline_scenario" in json_data["data"]
