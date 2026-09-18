"""AEGIS Model Deployment ORM Model."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, JSON
from packages.database.base import Base


class ModelDeploymentModel(Base):
    """Active or Historic Model Deployment Entity."""
    __tablename__ = "ml_deployments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    model_version_id = Column(String, nullable=False, index=True)
    environment = Column(String(50), nullable=False, default="STAGING")  # STAGING, PRODUCTION
    deployment_status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE, RETIRED
    endpoint_reference = Column(String(255), nullable=False)
    replica_config_json = Column(JSON, nullable=False, default=dict)
    deployed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    retired_at = Column(DateTime(timezone=True), nullable=True)
