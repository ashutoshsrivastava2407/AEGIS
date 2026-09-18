"""Contract Verification Tests for AEGIS REST API Envelopes."""

import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app


@pytest.mark.asyncio
async def test_api_v1_command_overview_contract():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/v1/command/overview")
        assert response.status_code == 200
        assert "x-correlation-id" in response.headers
        assert "x-request-id" in response.headers

        body = response.json()
        assert body["success"] is True
        assert "correlation_id" in body
        assert "timestamp" in body
        assert body["data"]["system_status"] == "OPERATIONAL"
