"""AEGIS Model Retraining Orchestrator."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from packages.database.models.ml_model import ModelModel, ModelVersionModel
from packages.database.models.ml_experiment import ExperimentModel
from services.ml.experiments.tracker import ExperimentTracker
from services.ml.training.trainer import TrainingEngine

logger = logging.getLogger("aegis.ml.retraining")


class RetrainingOrchestrator:
    """Triggers retraining requests and creates new experiment runs with promotion gates."""

    @staticmethod
    def trigger_retraining(
        session: Session,
        tenant_id: str,
        model_id: str,
        trigger_reason: str = "DRIFT_DETECTED",
        dataset_version: str = "2.0"
    ) -> Dict[str, Any]:
        """Trigger model retraining workflow, log new experiment run, and queued training job."""
        model = session.query(ModelModel).filter(ModelModel.id == model_id, ModelModel.tenant_id == tenant_id).first()
        if not model:
            raise ValueError(f"Model id '{model_id}' not found for tenant '{tenant_id}'.")

        # Find or create Retraining experiment
        exp_name = f"Retraining Pipeline - {model.name}"
        exp = session.query(ExperimentModel).filter(
            ExperimentModel.tenant_id == tenant_id,
            ExperimentModel.name == exp_name
        ).first()

        if not exp:
            exp = ExperimentTracker.create_experiment(
                session=session,
                tenant_id=tenant_id,
                name=exp_name,
                objective=f"Automated retraining triggered by {trigger_reason}"
            )

        # Log new run
        run = ExperimentTracker.log_run(
            session=session,
            experiment_id=exp.id,
            tenant_id=tenant_id,
            algorithm="RANDOM_FOREST_CLASSIFIER" if model.task_type == "CLASSIFICATION" else "RANDOM_FOREST_REGRESSOR",
            hyperparameters={"n_estimators": 20, "max_depth": 5},
            parameters={"trigger_reason": trigger_reason, "random_seed": 42},
            metrics={},
            artifacts={},
            dataset_version=dataset_version,
            status="RUNNING"
        )

        # Create training job
        job = TrainingEngine.create_job(
            session=session,
            tenant_id=tenant_id,
            experiment_id=exp.id,
            run_id=run.id,
            algorithm=run.algorithm,
            configuration={"hyperparameters": run.hyperparameters_json, "random_seed": 42}
        )

        logger.info("Triggered Retraining for model=%s trigger=%s job=%s", model_id, trigger_reason, job.id)
        return {
            "model_id": model_id,
            "experiment_id": exp.id,
            "run_id": run.id,
            "training_job_id": job.id,
            "trigger_reason": trigger_reason,
            "promotion_gate": "EXPLICIT_APPROVAL_REQUIRED",
        }
