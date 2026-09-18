"""Integration Test for End-to-End AEGIS Ingestion Pipeline."""

import pytest
from packages.security import UserContext
from services.data_platform.services import data_platform_service
from packages.storage import storage


@pytest.mark.asyncio
async def test_end_to_end_ingestion_pipeline():
    user = UserContext(
        user_id="usr_tester",
        tenant_id="tenant_qa_01",
        username="qa_operator",
        email="qa@aegis.enterprise",
        is_admin=True,
    )

    # 1. Register CSV Source with invalid rows
    source = await data_platform_service.register_source(
        name="Orders Ingestion Feed",
        source_type="CSV",
        config={"file_path": "data/fixtures/invalid_orders.csv"},
        user=user,
    )
    assert source["id"] is not None

    # 2. Trigger Pipeline Run
    result = await data_platform_service.trigger_ingestion(source["id"], user)
    assert result["status"] == "PARTIAL_SUCCESS"
    assert result["records_read"] == 5
    assert result["records_written"] == 3
    assert result["records_rejected"] == 2

    # 3. Verify Bronze Raw Object Storage
    bronze_exists = await storage.object_exists(result["bronze_key"])
    assert bronze_exists is True

    # 4. Verify Silver Clean Storage
    silver_exists = await storage.object_exists(result["silver_key"])
    assert silver_exists is True

    # 5. Verify Health Score & Quarantine
    assert result["health_score"]["overall_score"] < 100.0
    quarantine = await data_platform_service.list_quarantine(user)
    assert len(quarantine) >= 2

    # 6. Verify Lineage Graph
    lineage = await data_platform_service.get_lineage_dag("root", user)
    assert len(lineage["nodes"]) >= 3
    assert len(lineage["edges"]) >= 2
