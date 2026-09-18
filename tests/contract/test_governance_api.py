"""AEGIS Governance, Security, and Compliance REST API Contract Tests."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_governance_audit_api_contract():
    """Verify GET /api/v1/governance/audit contract."""
    res = client.get("/api/v1/governance/audit")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert "data" in json_data


def test_governance_policies_api_contract():
    """Verify GET /api/v1/governance/policies contract."""
    res = client.get("/api/v1/governance/policies")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["isolation_level"] == "STRICT_ROW_LEVEL"


def test_run_governed_pipeline_api_contract():
    """Verify POST /api/v1/governance/pipeline/run contract."""
    res = client.post("/api/v1/governance/pipeline/run", json={
        "action": "SCALE_SERVICE_WORKERS",
        "resource_id": "cluster-prod-01",
        "data_classification": "RESTRICTED"
    })
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "COMPLETED"
    assert json_data["data"]["audit_chain_verified"] is True


def test_identity_users_api_contract():
    """Verify GET /api/v1/identity/users contract."""
    res = client.get("/api/v1/identity/users")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) > 0


def test_identity_service_identities_api_contract():
    """Verify GET /api/v1/identity/services contract."""
    res = client.get("/api/v1/identity/services")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["identity_type"] == "WORKFLOW"


def test_security_events_api_contract():
    """Verify GET /api/v1/security/events contract."""
    res = client.get("/api/v1/security/events")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True


def test_compliance_posture_api_contract():
    """Verify GET /api/v1/compliance/posture contract."""
    res = client.get("/api/v1/compliance/posture")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["score_percent"] == 100.0
