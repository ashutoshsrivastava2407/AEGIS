"""Tests for AEGIS Command Center Extended Telemetry & Activity Router."""

import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app


@pytest.mark.asyncio
async def test_command_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/v1/command/health")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "health_score" in body["data"]
        assert "contributing_dimensions" in body["data"]


@pytest.mark.asyncio
async def test_command_metrics_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/v1/command/metrics?time_range=24h")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "event_ingestion_series" in body["data"]
        assert "inference_latencies" in body["data"]
        assert "decision_impact" in body["data"]


@pytest.mark.asyncio
async def test_command_activity_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/v1/command/activity?limit=10")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) <= 10


@pytest.mark.asyncio
async def test_command_readiness_gate():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/v1/command/readiness")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["overall_status"] == "READY_FOR_PRODUCTION"
        assert body["data"]["dimensions_evaluated_count"] == 19
