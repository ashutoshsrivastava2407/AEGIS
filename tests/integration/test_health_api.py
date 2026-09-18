"""Integration Tests for FastAPI Health Endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app


@pytest.mark.asyncio
async def test_health_live_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert data["service"] == "aegis-api"


@pytest.mark.asyncio
async def test_health_ready_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data
