"""AEGIS Model & Feature Drift Record ORM Model."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, Float, JSON
from packages.database.base import Base


class ModelDriftRecordModel(Base):
    """Statistical Feature & Prediction Drift Evaluation Record."""
    __tablename__ = "ml_drift_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    model_id = Column(String, nullable=False, index=True)
    feature_name = Column(String(100), nullable=False, index=True)
    reference_period = Column(String(100), nullable=False, default="BASELINE_TRAINING")
    current_period = Column(String(100), nullable=False, default="RECENT_INFERENCE_30D")
    method = Column(String(50), nullable=False, default="POPULATION_STABILITY_INDEX")  # PSI, KS_TEST, WASSERSTEIN_DISTANCE
    score = Column(Float, nullable=False, default=0.0)
    threshold = Column(Float, nullable=False, default=0.1)
    status = Column(String(30), nullable=False, default="NO_DRIFT")  # NO_DRIFT, DRIFT_DETECTED, INSUFFICIENT_DATA
    evidence_json = Column(JSON, nullable=False, default=dict)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
