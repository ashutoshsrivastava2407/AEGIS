"""AEGIS Autonomous Agent Platform REST API Contract Test Suite."""

from fastapi.testclient import TestClient
import pytest

from apps.api.main import app

client = TestClient(app)


def test_agents_overview_contract():
    """Verify /api/v1/agents/overview API response schema."""
    response = client.get("/api/v1/agents/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["platform_status"] == "ACTIVE"
    assert "total_agents" in data
    assert "total_governed_tools" in data
    assert "pending_human_approvals" in data


def test_agent_catalog_contract():
    """Verify /api/v1/agents/catalog list & create endpoints."""
    response = client.get("/api/v1/agents/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) >= 5

    # Create new agent
    create_res = client.post(
        "/api/v1/agents/catalog",
        json={
            "name": "Contract Test Agent",
            "agent_type": "DATA",
            "role_prompt": "Contract testing prompt",
            "description": "Agent created during contract test"
        }
    )
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["name"] == "Contract Test Agent"
    assert created_data["lifecycle_state"] == "DRAFT"


def test_agent_tools_contract():
    """Verify /api/v1/agents/tools endpoint returns catalog of governed tools."""
    response = client.get("/api/v1/agents/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) >= 10


def test_execute_agent_run_contract():
    """Verify POST /api/v1/agents/runs triggers multi-agent pipeline."""
    response = client.post(
        "/api/v1/agents/runs",
        json={
            "goal": "Contract test query for agent platform API",
            "agent_type": "SUPERVISOR"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "run_id" in data
    assert data["status"] in ["COMPLETED", "FAILED", "WAITING_APPROVAL"]
    assert "total_steps" in data
    assert "verification" in data
    assert "evaluation" in data
