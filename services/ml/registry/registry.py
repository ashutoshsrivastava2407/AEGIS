"""AEGIS Governed Model Registry Engine."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.ml_model import ModelModel, ModelVersionModel

logger = logging.getLogger("aegis.ml.registry")


class InvalidModelLifecycleTransitionError(Exception):
    """Raised when an invalid model status transition is requested."""
    pass


class ModelRegistryEngine:
    """Manages model registration, versioning, and strict state machine lifecycle transitions."""

    VALID_TRANSITIONS = {
        "DRAFT": ["EVALUATED", "RETIRED"],
        "EVALUATED": ["APPROVED", "RETIRED"],
        "APPROVED": ["STAGING", "PRODUCTION", "RETIRED"],
        "STAGING": ["PRODUCTION", "RETIRED"],
        "PRODUCTION": ["RETIRED"],
        "RETIRED": [],
    }

    @staticmethod
    def register_model(
        session: Session,
        tenant_id: str,
        name: str,
        task_type: str = "CLASSIFICATION",
        description: Optional[str] = None,
        owner: str = "ml_lead"
    ) -> ModelModel:
        """Register a new governed Machine Learning Model container."""
        model = ModelModel(
            tenant_id=tenant_id,
            name=name,
            description=description,
            task_type=task_type.upper(),
            owner=owner,
            status="ACTIVE",
            current_version=1,
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        logger.info("Registered Model id=%s name=%s task=%s tenant=%s", model.id, name, task_type, tenant_id)
        return model

    @staticmethod
    def create_model_version(
        session: Session,
        tenant_id: str,
        model_id: str,
        experiment_run_id: str,
        algorithm: str,
        hyperparameters: Dict[str, Any],
        artifact_reference: Dict[str, Any],
        evaluation_summary: Dict[str, Any],
        dataset_version: str = "1.0",
        feature_set_version: int = 1
    ) -> ModelVersionModel:
        """Create a new version under a registered Model entity."""
        model = session.query(ModelModel).filter(
            ModelModel.id == model_id,
            ModelModel.tenant_id == tenant_id
        ).first()

        if not model:
            raise ValueError(f"Model id '{model_id}' not found for tenant '{tenant_id}'.")

        existing_versions = session.query(ModelVersionModel).filter(
            ModelVersionModel.model_id == model_id
        ).count()

        version_num = existing_versions + 1
        model.current_version = version_num

        m_version = ModelVersionModel(
            model_id=model_id,
            tenant_id=tenant_id,
            version=version_num,
            experiment_run_id=experiment_run_id,
            dataset_version=dataset_version,
            feature_set_version=feature_set_version,
            algorithm=algorithm,
            hyperparameters_json=hyperparameters,
            artifact_reference_json=artifact_reference,
            evaluation_summary_json=evaluation_summary,
            status="DRAFT",
        )
        session.add(m_version)
        session.commit()
        session.refresh(m_version)
        logger.info("Created ModelVersion id=%s model=%s version=%d status=DRAFT", m_version.id, model_id, version_num)
        return m_version

    @classmethod
    def promote_model_version(
        cls,
        session: Session,
        tenant_id: str,
        version_id: str,
        target_status: str
    ) -> ModelVersionModel:
        """Promote model version status enforcing state machine transition rules:
        DRAFT -> EVALUATED -> APPROVED -> STAGING -> PRODUCTION -> RETIRED
        """
        target_upper = target_status.upper()
        m_version = session.query(ModelVersionModel).filter(
            ModelVersionModel.id == version_id,
            ModelVersionModel.tenant_id == tenant_id
        ).first()

        if not m_version:
            raise ValueError(f"ModelVersion id '{version_id}' not found for tenant '{tenant_id}'.")

        current_status = m_version.status.upper()
        allowed = cls.VALID_TRANSITIONS.get(current_status, [])

        if target_upper not in allowed:
            raise InvalidModelLifecycleTransitionError(
                f"Invalid Model Promotion Transition: Cannot transition from status '{current_status}' "
                f"to '{target_upper}'. Allowed target statuses from '{current_status}' are: {allowed}"
            )

        # If promoting to PRODUCTION, retire any existing PRODUCTION versions for this model
        if target_upper == "PRODUCTION":
            session.query(ModelVersionModel).filter(
                ModelVersionModel.model_id == m_version.model_id,
                ModelVersionModel.tenant_id == tenant_id,
                ModelVersionModel.status == "PRODUCTION",
                ModelVersionModel.id != version_id
            ).update({"status": "RETIRED"})

        m_version.status = target_upper
        m_version.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(m_version)
        logger.info("Promoted ModelVersion id=%s from %s to %s", version_id, current_status, target_upper)
        return m_version
