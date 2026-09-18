"""AEGIS Streaming REST API Contract Tests."""

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_streaming_overview_api_contract():
    """Verify GET /api/v1/streaming/overview endpoint contract."""
    response = client.get("/api/v1/streaming/overview")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "broker" in data
    assert "active_topics" in data
    assert "total_consumer_lag" in data
    assert "streaming_quality_score" in data


def test_streaming_topics_api_contract():
    """Verify POST /api/v1/streaming/topics and GET /api/v1/streaming/topics endpoints."""
    # Create topic
    create_payload = {
        "name": "test.contract.topic.v1",
        "partitions": 2,
        "description": "Contract test topic",
    }
    create_res = client.post("/api/v1/streaming/topics", json=create_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["name"] == "test.contract.topic.v1"
    assert created_data["partitions"] == 2

    # List topics
    list_res = client.get("/api/v1/streaming/topics")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert "topics" in list_data
    assert list_data["total"] >= 1


def test_produce_event_api_contract():
    """Verify POST /api/v1/streaming/topics/{topic_name}/produce endpoint contract."""
    topic_name = "test.contract.topic.v1"
    event_payload = {
        "event_type": "contract.test.event",
        "payload": {"key": "value", "count": 100},
    }
    res = client.post(f"/api/v1/streaming/topics/{topic_name}/produce", json=event_payload)
    assert res.status_code == 202
    data = res.json()
    assert data["status"] == "DELIVERED"
    assert "event_id" in data
    assert data["topic"] == topic_name


def test_streaming_consumer_groups_api_contract():
    """Verify GET /api/v1/streaming/consumers endpoint contract."""
    response = client.get("/api/v1/streaming/consumers")
    assert response.status_code == 200
    data = response.json()
    assert "consumer_groups" in data


def test_streaming_dlq_api_contract():
    """Verify GET /api/v1/streaming/dlq endpoint contract."""
    response = client.get("/api/v1/streaming/dlq")
    assert response.status_code == 200
    data = response.json()
    assert "dlq_records" in data


def test_streaming_quality_api_contract():
    """Verify GET /api/v1/streaming/quality endpoint contract."""
    response = client.get("/api/v1/streaming/quality")
    assert response.status_code == 200
    data = response.json()
    assert "quality_metrics" in data
