"""AEGIS Feature Store Registry."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.ml_feature import FeatureDefinitionModel, FeatureSetModel, FeatureSnapshotModel
from services.ml.features.transformations import FeatureTransformer
from services.ml.features.leakage_guard import LeakageGuard

logger = logging.getLogger("aegis.ml.features")


class FeatureStoreRegistry:
    """Manages feature registration, feature set composition, and point-in-time snapshots."""

    @staticmethod
    def register_feature(
        session: Session,
        tenant_id: str,
        name: str,
        transformation_definition: str,
        data_type: str = "FLOAT",
        entity_key: str = "entity_id",
        source_dataset_id: Optional[str] = None,
        source_columns: Optional[List[str]] = None,
        description: Optional[str] = None,
        owner: str = "ml_engineer"
    ) -> FeatureDefinitionModel:
        """Register or version a governed feature definition."""
        existing = session.query(FeatureDefinitionModel).filter(
            FeatureDefinitionModel.tenant_id == tenant_id,
            FeatureDefinitionModel.name == name
        ).first()

        version = (existing.version + 1) if existing else 1

        feature = FeatureDefinitionModel(
            tenant_id=tenant_id,
            name=name,
            description=description or f"Feature {name} v{version}",
            data_type=data_type.upper(),
            entity_key=entity_key,
            transformation_definition=transformation_definition,
            source_dataset_id=source_dataset_id,
            source_columns_json=source_columns or [],
            owner=owner,
            status="ACTIVE",
            version=version,
        )
        session.add(feature)
        session.commit()
        session.refresh(feature)
        logger.info("Registered FeatureDefinition id=%s name=%s version=%d tenant=%s", feature.id, name, version, tenant_id)
        return feature

    @staticmethod
    def create_feature_set(
        session: Session,
        tenant_id: str,
        name: str,
        feature_ids: List[str],
        target_column: Optional[str] = None,
        purpose: str = "TRAINING",
        description: Optional[str] = None,
        owner: str = "ml_engineer"
    ) -> FeatureSetModel:
        """Construct a reproducible feature set collection."""
        features = session.query(FeatureDefinitionModel).filter(
            FeatureDefinitionModel.id.in_(feature_ids),
            FeatureDefinitionModel.tenant_id == tenant_id
        ).all()

        feature_names = [f.name for f in features]
        if target_column:
            LeakageGuard.validate_target_leakage(feature_names, target_column)

        existing = session.query(FeatureSetModel).filter(
            FeatureSetModel.tenant_id == tenant_id,
            FeatureSetModel.name == name
        ).first()
        version = (existing.version + 1) if existing else 1

        feature_set = FeatureSetModel(
            tenant_id=tenant_id,
            name=name,
            description=description or f"Feature set {name} v{version}",
            feature_ids_json=feature_ids,
            version=version,
            source_dataset_versions_json={"dataset_v": "1.0"},
            purpose=purpose,
            owner=owner,
            status="ACTIVE",
        )
        session.add(feature_set)
        session.commit()
        session.refresh(feature_set)
        logger.info("Created FeatureSet id=%s name=%s version=%d tenant=%s", feature_set.id, name, version, tenant_id)
        return feature_set

    @staticmethod
    def record_snapshot(
        session: Session,
        tenant_id: str,
        feature_set_id: str,
        entity_id: str,
        feature_values: Dict[str, Any],
        source_version: str = "1.0"
    ) -> FeatureSnapshotModel:
        """Persist point-in-time feature snapshot for offline training and online serving audit."""
        snapshot = FeatureSnapshotModel(
            tenant_id=tenant_id,
            feature_set_id=feature_set_id,
            entity_id=entity_id,
            feature_values_json=feature_values,
            event_timestamp=datetime.now(timezone.utc),
            feature_version=1,
            source_version=source_version,
        )
        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)
        return snapshot
