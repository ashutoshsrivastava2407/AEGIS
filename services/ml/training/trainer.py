"""AEGIS Asynchronous Model Training Engine."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session

from packages.database.models.ml_training import TrainingJobModel
from services.ml.training.models_provider import ModelProviderFactory
from services.ml.training.artifact_store import artifact_store

logger = logging.getLogger("aegis.ml.training")


class TrainingEngine:
    """Manages asynchronous training job lifecycle and model artifact generation."""

    @staticmethod
    def create_job(
        session: Session,
        tenant_id: str,
        experiment_id: str,
        run_id: str,
        algorithm: str,
        configuration: Dict[str, Any],
        dataset_id: Optional[str] = None,
        feature_set_id: Optional[str] = None
    ) -> TrainingJobModel:
        """Create a new training job entry in QUEUED state."""
        job = TrainingJobModel(
            tenant_id=tenant_id,
            experiment_id=experiment_id,
            run_id=run_id,
            dataset_id=dataset_id,
            feature_set_id=feature_set_id,
            algorithm=algorithm,
            configuration_json=configuration,
            status="QUEUED",
            resource_metadata_json={"cpu_cores": 2, "memory_mb": 4096},
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        logger.info("Created TrainingJob id=%s algorithm=%s tenant=%s", job.id, algorithm, tenant_id)
        return job

    @staticmethod
    def execute_job(
        session: Session,
        job_id: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        model_id: str,
        version: int = 1
    ) -> Tuple[TrainingJobModel, Any, Dict[str, Any]]:
        """Execute real model training, update job status, and save serialized artifact."""
        job = session.query(TrainingJobModel).filter(TrainingJobModel.id == job_id).first()
        if not job:
            raise ValueError(f"TrainingJob id '{job_id}' not found.")

        job.status = "RUNNING"
        job.started_at = datetime.now(timezone.utc)
        session.commit()

        try:
            config = job.configuration_json or {}
            hyperparams = config.get("hyperparameters", {})
            seed = config.get("random_seed", 42)

            model, train_meta = ModelProviderFactory.train_model(
                algorithm=job.algorithm,
                X=X_train,
                y=y_train,
                hyperparameters=hyperparams,
                random_seed=seed,
            )

            # Persist artifact
            artifact_meta = artifact_store.save_artifact(model, model_id=model_id, version=version)

            job.status = "COMPLETED"
            job.completed_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(job)

            logger.info("TrainingJob id=%s COMPLETED checksum=%s", job.id, artifact_meta["checksum"])
            return job, model, artifact_meta

        except Exception as e:
            job.status = "FAILED"
            job.completed_at = datetime.now(timezone.utc)
            job.error_info = str(e)
            session.commit()
            logger.error("TrainingJob id=%s FAILED: %s", job.id, str(e))
            raise
