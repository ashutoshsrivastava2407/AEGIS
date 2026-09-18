"""Data Platform Domain Application Service."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from packages.security import UserContext, audit_recorder
from services.data_platform.connectors import get_connector
from services.data_platform.ingestion import ingestion_engine
from services.data_platform.lineage import lineage_engine
from packages.observability import logger


class DataPlatformService:
    """Central service managing data sources, ingestion runs, datasets, quality checks, quarantine, and lineage DAGs."""

    def __init__(self) -> None:
        # In-memory tenant state store backing persistent database handlers
        self._sources: Dict[str, Dict[str, Any]] = {}
        self._datasets: Dict[str, Dict[str, Any]] = {}
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._contracts: Dict[str, Dict[str, Any]] = {}
        self._quarantine: Dict[str, List[Dict[str, Any]]] = {}
        self._lineage_edges: List[Dict[str, Any]] = []

    async def register_source(self, name: str, source_type: str, config: Dict[str, Any], user: UserContext) -> Dict[str, Any]:
        connector = get_connector(source_type)
        valid, msg = connector.validate_config(config)
        if not valid:
            raise ValueError(f"Invalid source configuration: {msg}")

        source_id = f"src_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        source = {
            "id": source_id,
            "tenant_id": user.tenant_id,
            "name": name,
            "source_type": source_type.upper(),
            "config_metadata": {k: ("***" if "pass" in k or "secret" in k or "key" in k else v) for k, v in config.items()},
            "raw_config": config,
            "status": "ACTIVE",
            "created_by": user.username,
            "created_at": now,
            "last_tested_at": now,
            "last_successful_ingestion_at": None,
            "last_error": None,
            "version": 1,
        }

        self._sources[source_id] = source

        audit_recorder.record_event(
            event_type="DATA_SOURCE_CREATED",
            actor_id=user.user_id,
            tenant_id=user.tenant_id,
            resource_id=source_id,
            action="CREATE",
            status="SUCCESS",
            details={"name": name, "type": source_type},
        )

        return source

    async def list_sources(self, user: UserContext) -> List[Dict[str, Any]]:
        return [s for s in self._sources.values() if s.get("tenant_id") == user.tenant_id]

    async def test_source(self, source_id: str, user: UserContext) -> Dict[str, Any]:
        source = self._sources.get(source_id)
        if not source or source.get("tenant_id") != user.tenant_id:
            raise ValueError("Data source not found")

        connector = get_connector(source["source_type"])
        ok, msg = await connector.test_connection(source.get("raw_config", {}))

        source["last_tested_at"] = datetime.now(timezone.utc).isoformat()
        if not ok:
            source["last_error"] = msg

        return {"source_id": source_id, "success": ok, "message": msg}

    async def trigger_ingestion(self, source_id: str, user: UserContext, gold_transform: Dict[str, Any] = None) -> Dict[str, Any]:
        source = self._sources.get(source_id)
        if not source or source.get("tenant_id") != user.tenant_id:
            raise ValueError("Data source not found")

        result = await ingestion_engine.execute_ingestion_run(
            tenant_id=user.tenant_id,
            source_id=source_id,
            source_name=source["name"],
            source_type=source["source_type"],
            config=source.get("raw_config", {}),
            gold_transform_config=gold_transform,
        )

        run_id = result["run_id"]
        dataset_id = result["dataset_id"]

        # Register Ingestion Job
        self._jobs[run_id] = result
        source["last_successful_ingestion_at"] = datetime.now(timezone.utc).isoformat()

        # Register Catalog Datasets for Bronze, Silver, Gold
        now = datetime.now(timezone.utc).isoformat()
        self._datasets[f"{dataset_id}_bronze"] = {
            "id": f"{dataset_id}_bronze",
            "tenant_id": user.tenant_id,
            "name": f"{source['name']} (Raw Bronze)",
            "layer": "BRONZE",
            "source_id": source_id,
            "record_count": result["records_read"],
            "quality_score": 100.0,
            "freshness": "LIVE",
            "storage_path": result["bronze_key"],
            "updated_at": now,
        }

        self._datasets[f"{dataset_id}_silver"] = {
            "id": f"{dataset_id}_silver",
            "tenant_id": user.tenant_id,
            "name": f"{source['name']} (Cleaned Silver)",
            "layer": "SILVER",
            "source_id": source_id,
            "record_count": result["records_written"],
            "quality_score": result["health_score"]["overall_score"],
            "freshness": "UP_TO_DATE",
            "storage_path": result["silver_key"],
            "updated_at": now,
        }

        if result.get("gold_key"):
            self._datasets[f"{dataset_id}_gold"] = {
                "id": f"{dataset_id}_gold",
                "tenant_id": user.tenant_id,
                "name": f"{source['name']} (Analytical Gold)",
                "layer": "GOLD",
                "source_id": source_id,
                "record_count": result["records_written"],
                "quality_score": result["health_score"]["overall_score"],
                "freshness": "UP_TO_DATE",
                "storage_path": result["gold_key"],
                "updated_at": now,
            }

        # Save Quarantine Records
        if result.get("quarantined_records"):
            if dataset_id not in self._quarantine:
                self._quarantine[dataset_id] = []
            self._quarantine[dataset_id].extend(result["quarantined_records"])

        # Persist Lineage Edges
        self._lineage_edges.extend([
            {
                "upstream_entity_id": source_id,
                "upstream_entity_type": "SOURCE",
                "downstream_entity_id": f"{dataset_id}_bronze",
                "downstream_entity_type": "DATASET",
                "relationship_type": "INGESTS_TO_BRONZE",
                "execution_run_id": run_id,
            },
            {
                "upstream_entity_id": f"{dataset_id}_bronze",
                "upstream_entity_type": "DATASET",
                "downstream_entity_id": f"{dataset_id}_silver",
                "downstream_entity_type": "DATASET",
                "relationship_type": "CLEANS_TO_SILVER",
                "execution_run_id": run_id,
            },
        ])

        if result.get("gold_key"):
            self._lineage_edges.append({
                "upstream_entity_id": f"{dataset_id}_silver",
                "upstream_entity_type": "DATASET",
                "downstream_entity_id": f"{dataset_id}_gold",
                "downstream_entity_type": "DATASET",
                "relationship_type": "TRANSFORMS_TO_GOLD",
                "execution_run_id": run_id,
            })

        return result

    async def list_jobs(self, user: UserContext) -> List[Dict[str, Any]]:
        return [j for j in self._jobs.values() if j.get("tenant_id") == user.tenant_id]

    async def list_datasets(self, layer: Optional[str], user: UserContext) -> List[Dict[str, Any]]:
        ds_list = [d for d in self._datasets.values() if d.get("tenant_id") == user.tenant_id]
        if layer and layer.upper() != "ALL":
            ds_list = [d for d in ds_list if d.get("layer") == layer.upper()]
        return ds_list

    async def get_dataset_quality(self, dataset_id: str, user: UserContext) -> Dict[str, Any]:
        # Find job for dataset
        matching_jobs = [j for j in self._jobs.values() if j.get("dataset_id") in dataset_id or dataset_id in j.get("dataset_id", "")]
        if matching_jobs:
            latest = matching_jobs[-1]
            return {
                "dataset_id": dataset_id,
                "health_score": latest["health_score"],
                "quality_results": latest["quality_results"],
            }

        return {
            "dataset_id": dataset_id,
            "health_score": {"overall_score": 100.0, "status": "HEALTHY", "dimension_scores": {}},
            "quality_results": [],
        }

    async def get_lineage_dag(self, resource_id: str, user: UserContext) -> Dict[str, Any]:
        return lineage_engine.build_graph(self._lineage_edges)

    async def list_quarantine(self, user: UserContext) -> List[Dict[str, Any]]:
        all_q = []
        for records in self._quarantine.values():
            all_q.extend(records)
        return all_q


data_platform_service = DataPlatformService()
