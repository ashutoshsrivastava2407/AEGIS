"""AEGIS Production Operations REST API Contract Tests."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_operations_overview_api_contract():
    """Verify GET /api/v1/operations/overview contract."""
    res = client.get("/api/v1/operations/overview")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "OPERATIONAL"


def test_operations_services_api_contract():
    """Verify GET /api/v1/operations/services contract."""
    res = client.get("/api/v1/operations/services")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert isinstance(json_data["data"], list)


def test_operations_metrics_summary_api_contract():
    """Verify GET /api/v1/operations/metrics/summary contract."""
    res = client.get("/api/v1/operations/metrics/summary")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "p50" in json_data["data"]
    assert "p99" in json_data["data"]


def test_operations_slo_api_contract():
    """Verify GET /api/v1/operations/slo contract."""
    res = client.get("/api/v1/operations/slo")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True


def test_operations_incidents_api_contract():
    """Verify GET /api/v1/operations/incidents contract."""
    res = client.get("/api/v1/operations/incidents")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True


def test_operations_remediation_api_contract():
    """Verify POST /api/v1/operations/remediation/execute contract."""
    res = client.post("/api/v1/operations/remediation/execute", json={
        "action": "RESTART_POD",
        "service_id": "aegis-api",
        "parameters": {"risk_level": "MEDIUM"}
    })
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["policy_decision"] == "ALLOW"
    assert json_data["data"]["execution_status"] == "SUCCESS"


def test_operations_recovery_backups_api_contract():
    """Verify GET /api/v1/operations/recovery/backups contract."""
    res = client.get("/api/v1/operations/recovery/backups")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True


def test_operations_finops_summary_api_contract():
    """Verify GET /api/v1/operations/finops/summary contract."""
    res = client.get("/api/v1/operations/finops/summary")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "total_cost_usd" in json_data["data"]
