"""AEGIS Analytics Platform REST API Contract Tests."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_analytics_overview_contract():
    """Verify GET /api/v1/analytics/overview endpoint contract."""
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "total_analytical_datasets" in data
    assert "total_metrics" in data
    assert "active_anomalies" in data
    assert "open_insights" in data


def test_analytics_datasets_contract():
    """Verify GET and POST /api/v1/analytics/datasets endpoints contract."""
    # List datasets
    list_res = client.get("/api/v1/analytics/datasets")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert "datasets" in list_data
    assert "total" in list_data

    # Create dataset
    create_payload = {
        "name": "Contract Test Dataset",
        "description": "Dataset for REST contract testing",
        "source_layer": "GOLD",
        "schema_json": {"id": "INTEGER", "value": "FLOAT"},
    }
    create_res = client.post("/api/v1/analytics/datasets", json=create_payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["name"] == "Contract Test Dataset"
    assert "id" in created


def test_analytics_metrics_contract():
    """Verify GET and POST /api/v1/analytics/metrics endpoints contract."""
    # Create dataset first
    ds_res = client.post("/api/v1/analytics/datasets", json={
        "name": "Metric Test Dataset",
    })
    ds_id = ds_res.json()["id"]

    # Create metric
    metric_payload = {
        "name": "Contract Test Metric",
        "source_dataset_id": ds_id,
        "aggregation_type": "SUM",
        "calculation_formula": "SUM(value)",
        "time_grain": "DAILY",
    }
    create_res = client.post("/api/v1/analytics/metrics", json=metric_payload)
    assert create_res.status_code == 201
    metric_data = create_res.json()
    assert metric_data["name"] == "Contract Test Metric"

    # List metrics
    list_res = client.get("/api/v1/analytics/metrics")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1

    # Evaluate metric
    eval_res = client.post(f"/api/v1/analytics/metrics/{metric_data['id']}/evaluate", json={
        "history": [10.0, 15.0, 20.0, 25.0, 30.0]
    })
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert "metric_id" in eval_data
    assert "metric_name" in eval_data
    assert "trend" in eval_data
    assert "value" in eval_data


def test_analytics_query_execution_contract():
    """Verify POST /api/v1/analytics/query AST SQL Guard execution contract."""
    query_payload = {
        "sql_text": "SELECT * FROM gold_contract_test",
        "user_id": "test_analyst",
    }
    res = client.post("/api/v1/analytics/query", json=query_payload)
    assert res.status_code in [200, 403, 400]

    # Test forbidden query rejection
    forbidden_payload = {
        "sql_text": "DROP TABLE gold_contract_test",
        "user_id": "attacker",
    }
    forbidden_res = client.post("/api/v1/analytics/query", json=forbidden_payload)
    assert forbidden_res.status_code == 403
    assert "Security Guard" in forbidden_res.json()["detail"]


def test_analytics_dashboards_contract():
    """Verify GET and POST /api/v1/analytics/dashboards endpoints contract."""
    payload = {
        "title": "Executive Financial Dashboard",
        "description": "Key financial performance indicators",
    }
    create_res = client.post("/api/v1/analytics/dashboards", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["title"] == "Executive Financial Dashboard"

    list_res = client.get("/api/v1/analytics/dashboards")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


def test_analytics_anomalies_and_insights_contract():
    """Verify GET /api/v1/analytics/anomalies and /insights endpoints contract."""
    anomalies_res = client.get("/api/v1/analytics/anomalies")
    assert anomalies_res.status_code == 200
    assert "anomalies" in anomalies_res.json()

    insights_res = client.get("/api/v1/analytics/insights")
    assert insights_res.status_code == 200
    assert "insights" in insights_res.json()


def test_analytics_alerts_contract():
    """Verify GET and POST /api/v1/analytics/alerts/rules endpoints contract."""
    rules_res = client.get("/api/v1/analytics/alerts/rules")
    assert rules_res.status_code == 200
    assert "alert_rules" in rules_res.json()

    events_res = client.get("/api/v1/analytics/alerts/events")
    assert events_res.status_code == 200
    assert "alert_events" in events_res.json()
