"""AEGIS Feature Store ORM Models."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from packages.database.base import Base


class FeatureDefinitionModel(Base):
    """Governed Feature Definition with versioning and transformation spec."""
    __tablename__ = "ml_feature_definitions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    data_type = Column(String(50), nullable=False, default="FLOAT")  # FLOAT, INT, STRING, BOOLEAN, TIMESTAMP
    entity_key = Column(String(100), nullable=False, default="entity_id")
    transformation_definition = Column(Text, nullable=False)  # Formula or transformation spec
    source_dataset_id = Column(String, nullable=True, index=True)
    source_columns_json = Column(JSON, nullable=False, default=list)
    owner = Column(String(100), nullable=False, default="ml_engineer")
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, DEPRECATED, ARCHIVED
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class FeatureSetModel(Base):
    """Reproducible collection of feature definitions."""
    __tablename__ = "ml_feature_sets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    feature_ids_json = Column(JSON, nullable=False, default=list)  # List of FeatureDefinition IDs
    version = Column(Integer, nullable=False, default=1)
    source_dataset_versions_json = Column(JSON, nullable=False, default=dict)
    purpose = Column(String(100), nullable=False, default="TRAINING")  # TRAINING, INFERENCE, BENCHMARK
    owner = Column(String(100), nullable=False, default="ml_engineer")
    status = Column(String(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class FeatureSnapshotModel(Base):
    """Point-in-time feature snapshot for offline training and serving audit."""
    __tablename__ = "ml_feature_snapshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    feature_set_id = Column(String, nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    feature_values_json = Column(JSON, nullable=False, default=dict)  # {feature_name: value}
    event_timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    feature_version = Column(Integer, nullable=False, default=1)
    source_version = Column(String(50), nullable=False, default="1.0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
