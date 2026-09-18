"""AEGIS Model Inference Audit Log ORM Model."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, Float, JSON
from packages.database.base import Base


class ModelInferenceLogModel(Base):
    """Real-time online and batch prediction inference log."""
    __tablename__ = "ml_inference_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    model_version_id = Column(String, nullable=False, index=True)
    feature_set_id = Column(String, nullable=True, index=True)
    inference_type = Column(String(20), nullable=False, default="ONLINE")  # ONLINE, BATCH
    input_payload_json = Column(JSON, nullable=False, default=dict)
    prediction_result_json = Column(JSON, nullable=False, default=dict)
    latency_ms = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="SUCCESS")  # SUCCESS, FAILED
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
