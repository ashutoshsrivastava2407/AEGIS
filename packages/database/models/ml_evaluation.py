"""AEGIS Model Evaluation Record ORM Model."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, Integer, JSON
from packages.database.base import Base


class ModelEvaluationModel(Base):
    """Formal Model Evaluation Execution Record."""
    __tablename__ = "ml_evaluations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    model_id = Column(String, nullable=False, index=True)
    model_version = Column(Integer, nullable=False, default=1)
    dataset_version = Column(String(50), nullable=False, default="1.0")
    metrics_json = Column(JSON, nullable=False, default=dict)  # {accuracy: 0.95, f1: 0.94, mae: 1.2, ...}
    evaluation_config_json = Column(JSON, nullable=False, default=dict)  # {task_type: ..., test_samples: ...}
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
