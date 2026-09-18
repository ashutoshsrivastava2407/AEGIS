"""AEGIS ML Experiment & Run Tracking ORM Models."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from packages.database.base import Base


class ExperimentModel(Base):
    """ML Experiment Container."""
    __tablename__ = "ml_experiments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    objective = Column(String(255), nullable=False, default="Maximize Model F1-Score")
    owner = Column(String(100), nullable=False, default="ml_scientist")
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, COMPLETED, ARCHIVED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ExperimentRunModel(Base):
    """Reproducible ML Training Experiment Run."""
    __tablename__ = "ml_experiment_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String, nullable=False, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    dataset_version = Column(String(50), nullable=False, default="1.0")
    feature_set_version = Column(Integer, nullable=False, default=1)
    algorithm = Column(String(100), nullable=False)  # Random_Forest, Logistic_Regression, Linear_Regression, etc.
    hyperparameters_json = Column(JSON, nullable=False, default=dict)
    parameters_json = Column(JSON, nullable=False, default=dict)  # seed, test_split, etc.
    metrics_json = Column(JSON, nullable=False, default=dict)  # {accuracy: 0.95, f1: 0.94, ...}
    artifacts_json = Column(JSON, nullable=False, default=dict)  # {model_checksum: "...", size: 1024}
    status = Column(String(20), nullable=False, default="RUNNING")  # RUNNING, COMPLETED, FAILED, CANCELLED
    failure_reason = Column(Text, nullable=True)
    training_started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    training_completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
