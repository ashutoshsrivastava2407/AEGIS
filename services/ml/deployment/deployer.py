"""AEGIS Model Deployment Manager."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.ml_deployment import ModelDeploymentModel
from packages.database.models.ml_model import ModelVersionModel

logger = logging.getLogger("aegis.ml.deployment")


class DeploymentManager:
    """Manages staging and production deployments for verified model versions."""

    @staticmethod
    def create_deployment(
        session: Session,
        tenant_id: str,
        model_version_id: str,
        environment: str = "PRODUCTION",
        replica_config: Optional[Dict[str, Any]] = None
    ) -> ModelDeploymentModel:
        """Deploy a promoted model version to an active serving environment."""
        m_version = session.query(ModelVersionModel).filter(
            ModelVersionModel.id == model_version_id,
            ModelVersionModel.tenant_id == tenant_id
        ).first()

        if not m_version:
            raise ValueError(f"ModelVersion id '{model_version_id}' not found for tenant '{tenant_id}'.")

        # Verify promotion status requirement
        if m_version.status not in ("APPROVED", "STAGING", "PRODUCTION"):
            raise ValueError(
                f"Deployment Rejected: ModelVersion status is '{m_version.status}'. "
                "Only APPROVED, STAGING, or PRODUCTION model versions can be deployed."
            )

        env_upper = environment.upper()
        endpoint_ref = f"/api/v1/ml/models/{m_version.model_id}/versions/{m_version.version}/predict"

        # Retire existing active deployments in the same environment for this model
        active_deployments = session.query(ModelDeploymentModel).filter(
            ModelDeploymentModel.tenant_id == tenant_id,
            ModelDeploymentModel.environment == env_upper,
            ModelDeploymentModel.deployment_status == "ACTIVE"
        ).all()

        for d in active_deployments:
            d.deployment_status = "RETIRED"
            d.retired_at = datetime.now(timezone.utc)

        deployment = ModelDeploymentModel(
            tenant_id=tenant_id,
            model_version_id=model_version_id,
            environment=env_upper,
            deployment_status="ACTIVE",
            endpoint_reference=endpoint_ref,
            replica_config_json=replica_config or {"replicas": 2, "timeout_ms": 5000},
            deployed_at=datetime.now(timezone.utc),
        )
        session.add(deployment)
        session.commit()
        session.refresh(deployment)
        logger.info("Created Deployment id=%s model_version=%s env=%s endpoint=%s", deployment.id, model_version_id, env_upper, endpoint_ref)
        return deployment
