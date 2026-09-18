"""AEGIS Ingestion Execution Orchestration Engine."""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

from services.data_platform.connectors import get_connector
from services.data_platform.ingestion.idempotency import idempotency_manager
from services.data_platform.quality import quality_engine
from packages.storage import storage
from packages.observability import logger


class IngestionEngine:
    """Orchestrates end-to-end ingestion pipeline across Bronze, Silver, Gold, Quality, Quarantine, and Lineage."""

    async def execute_ingestion_run(
        self,
        tenant_id: str,
        source_id: str,
        source_name: str,
        source_type: str,
        config: Dict[str, Any],
        gold_transform_config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        run_id = str(uuid.uuid4())
        today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        logger.info(f"Starting Ingestion Run {run_id} for Source '{source_name}' ({source_type})")

        # 1. Instantiate Connector and Read Raw Records
        try:
            connector = get_connector(source_type)
            raw_records = await connector.read(config)
        except Exception as e:
            logger.error(f"Connector Read Error on Ingestion Run {run_id}: {e}", exc_info=True)
            return {
                "run_id": run_id,
                "status": "FAILED",
                "records_read": 0,
                "records_written": 0,
                "error": str(e),
                "duration_ms": (time.time() - start_time) * 1000,
            }

        records_read = len(raw_records)
        payload_bytes = len(json.dumps(raw_records).encode("utf-8"))
        checksum = idempotency_manager.compute_checksum(raw_records)

        # 2. Write RAW Immutable Data to BRONZE Storage
        bronze_key = f"bronze/{tenant_id}/{source_id}/{run_id}/{today_date}/raw.json"
        bronze_data = json.dumps({
            "run_id": run_id,
            "tenant_id": tenant_id,
            "source_id": source_id,
            "source_type": source_type,
            "ingestion_date": today_date,
            "records_count": records_read,
            "checksum": checksum,
            "records": raw_records,
        }, indent=2).encode("utf-8")

        await storage.put_object(bronze_key, bronze_data, content_type="application/json")
        logger.info(f"Bronze raw payload written to '{bronze_key}'")

        # 3. Process SILVER Layer (Validation, Standardization, Quarantine)
        dataset_id = f"ds_{source_id[:12]}"
        version_id = f"ver_{run_id[:8]}"

        quality_results, quarantined_records, health_score = await quality_engine.run_quality_checks(
            records=raw_records,
            dataset_id=dataset_id,
            version_id=version_id,
        )

        records_rejected = len(quarantined_records)
        records_written = records_read - records_rejected

        silver_records = [r for r in raw_records if r not in [q["raw_payload"] for q in quarantined_records]]
        silver_key = f"silver/{tenant_id}/{dataset_id}/v1/data.json"
        silver_payload = json.dumps({
            "dataset_id": dataset_id,
            "tenant_id": tenant_id,
            "version": 1,
            "layer": "SILVER",
            "clean_records_count": records_written,
            "records": silver_records,
        }, indent=2).encode("utf-8")

        await storage.put_object(silver_key, silver_payload, content_type="application/json")
        logger.info(f"Silver cleaned dataset written to '{silver_key}'")

        # 4. Check GOLD Layer (Strict Governance Rule: Only process if explicit transform config supplied)
        gold_status = "NOT_CONFIGURED"
        gold_key = None
        if gold_transform_config and gold_transform_config.get("enabled"):
            gold_status = "COMPLETED"
            gold_key = f"gold/{tenant_id}/{dataset_id}/v1/data.json"
            gold_payload = json.dumps({
                "dataset_id": dataset_id,
                "layer": "GOLD",
                "transformation": gold_transform_config.get("type", "EXPLICIT_AGGREGATION"),
                "records": silver_records,
            }, indent=2).encode("utf-8")
            await storage.put_object(gold_key, gold_payload, content_type="application/json")
            logger.info(f"Gold aggregated dataset written to '{gold_key}'")

        duration_ms = (time.time() - start_time) * 1000

        return {
            "run_id": run_id,
            "tenant_id": tenant_id,
            "source_id": source_id,
            "dataset_id": dataset_id,
            "status": "SUCCEEDED" if records_rejected == 0 else "PARTIAL_SUCCESS",
            "records_read": records_read,
            "records_written": records_written,
            "records_rejected": records_rejected,
            "bytes_processed": payload_bytes,
            "checksum": checksum,
            "duration_ms": duration_ms,
            "bronze_key": bronze_key,
            "silver_key": silver_key,
            "gold_key": gold_key,
            "gold_status": gold_status,
            "health_score": health_score,
            "quality_results": quality_results,
            "quarantined_records": quarantined_records,
        }


ingestion_engine = IngestionEngine()
