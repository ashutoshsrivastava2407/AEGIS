"""AEGIS ML Training Job ORM Model."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, JSON
from packages.database.base import Base


class TrainingJobModel(Base):
    """Asynchronous ML Model Training Job Execution."""
    __tablename__ = "ml_training_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    experiment_id = Column(String, nullable=False, index=True)
    run_id = Column(String, nullable=False, index=True)
    dataset_id = Column(String, nullable=True, index=True)
    feature_set_id = Column(String, nullable=True, index=True)
    algorithm = Column(String(100), nullable=False)
    configuration_json = Column(JSON, nullable=False, default=dict)
    status = Column(String(20), nullable=False, default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    resource_metadata_json = Column(JSON, nullable=False, default=dict)  # CPU/Memory resource metadata
    error_info = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
