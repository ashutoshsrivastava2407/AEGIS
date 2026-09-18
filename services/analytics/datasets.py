"""AEGIS Analytical Dataset Registry & Provenance.

Manages governed analytical datasets and integrates lineage graph edges.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.analytical_dataset import AnalyticalDatasetModel
from packages.database.models.lineage import LineageEdgeModel

logger = logging.getLogger("aegis.analytics.datasets")


class AnalyticalDatasetRegistry:
    """Manages analytical dataset registrations and lineage provenance."""

    @staticmethod
    def register_dataset(
        session: Session,
        tenant_id: str,
        name: str,
        description: Optional[str],
        source_dataset_id: Optional[str],
        source_layer: str = "GOLD",
        schema_json: Optional[Dict[str, Any]] = None,
        owner: str = "analytics_team",
        refresh_info: Optional[Dict[str, Any]] = None
    ) -> AnalyticalDatasetModel:
        """Register a governed analytical dataset with lineage edge linkage."""
        dataset = AnalyticalDatasetModel(
            tenant_id=tenant_id,
            name=name,
            description=description,
            source_dataset_id=source_dataset_id,
            source_layer=source_layer,
            version="1.0.0",
            schema_json=schema_json or {},
            owner=owner,
            status="ACTIVE",
            refresh_info=refresh_info or {"mode": "BATCH", "schedule": "@daily"},
        )
        session.add(dataset)
        session.commit()
        session.refresh(dataset)

        # Record lineage provenance edge if source dataset exists
        if source_dataset_id:
            edge = LineageEdgeModel(
                tenant_id=tenant_id,
                source_resource_id=source_dataset_id,
                target_resource_id=dataset.id,
                edge_type="PRODUCING_ANALYTICAL_DATASET",
                metadata_json={"source_layer": source_layer, "target_name": name},
            )
            session.add(edge)
            session.commit()

        logger.info("Registered AnalyticalDataset id=%s name=%s tenant=%s", dataset.id, name, tenant_id)
        return dataset

    @staticmethod
    def list_datasets(session: Session, tenant_id: str) -> List[AnalyticalDatasetModel]:
        """List all active analytical datasets for tenant."""
        return (
            session.query(AnalyticalDatasetModel)
            .filter(
                AnalyticalDatasetModel.tenant_id == tenant_id,
                AnalyticalDatasetModel.status == "ACTIVE"
            )
            .all()
        )
