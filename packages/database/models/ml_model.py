"""AEGIS Governed Model Registry ORM Models."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from packages.database.base import Base


class ModelModel(Base):
    """Governed Machine Learning Model entity."""
    __tablename__ = "ml_models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    task_type = Column(String(50), nullable=False, default="CLASSIFICATION")  # CLASSIFICATION, REGRESSION, FORECASTING, ANOMALY_DETECTION
    owner = Column(String(100), nullable=False, default="ml_lead")
    status = Column(String(20), nullable=False, default="ACTIVE")
    current_version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ModelVersionModel(Base):
    """Governed Version of a Machine Learning Model."""
    __tablename__ = "ml_model_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String, nullable=False, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    experiment_run_id = Column(String, nullable=False, index=True)
    dataset_version = Column(String(50), nullable=False, default="1.0")
    feature_set_version = Column(Integer, nullable=False, default=1)
    algorithm = Column(String(100), nullable=False)
    hyperparameters_json = Column(JSON, nullable=False, default=dict)
    artifact_reference_json = Column(JSON, nullable=False, default=dict)  # {checksum, size, uri, format}
    evaluation_summary_json = Column(JSON, nullable=False, default=dict)  # {primary_metric: 0.95, ...}
    status = Column(String(20), nullable=False, default="DRAFT")  # DRAFT -> EVALUATED -> APPROVED -> STAGING -> PRODUCTION -> RETIRED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
