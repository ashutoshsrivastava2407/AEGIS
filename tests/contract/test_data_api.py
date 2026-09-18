"""Contract Verification Tests for Data Platform REST APIs."""

import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app


@pytest.mark.asyncio
async def test_data_sources_and_ingestion_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Register Source
        res_create = await client.post(
            "/api/v1/data/sources",
            json={
                "name": "API Test Feed",
                "source_type": "CSV",
                "config": {"file_path": "data/fixtures/valid_orders.csv"},
            },
        )
        assert res_create.status_code == 200
        source = res_create.json()["data"]
        source_id = source["id"]

        # Test Connection
        res_test = await client.post(f"/api/v1/data/sources/{source_id}/test")
        assert res_test.status_code == 200
        assert res_test.json()["data"]["success"] is True

        # Trigger Ingestion
        res_ingest = await client.post(
            "/api/v1/data/ingestions",
            json={"source_id": source_id},
        )
        assert res_ingest.status_code == 200
        job = res_ingest.json()["data"]
        assert job["status"] == "SUCCEEDED"
        assert job["records_read"] == 5

        # List Datasets
        res_ds = await client.get("/api/v1/data/datasets")
        assert res_ds.status_code == 200
        datasets = res_ds.json()["data"]
        assert len(datasets) >= 2

        # Get Lineage DAG
        res_lin = await client.get(f"/api/v1/data/datasets/{source_id}/lineage")
        assert res_lin.status_code == 200
        graph = res_lin.json()["data"]
        assert len(graph["nodes"]) >= 3
