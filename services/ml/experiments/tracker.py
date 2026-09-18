"""AEGIS ML Experiment Tracker."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.ml_experiment import ExperimentModel, ExperimentRunModel

logger = logging.getLogger("aegis.ml.experiments")


class ExperimentTracker:
    """Manages experiment creation and reproducible run metadata logging."""

    @staticmethod
    def create_experiment(
        session: Session,
        tenant_id: str,
        name: str,
        description: Optional[str] = None,
        objective: str = "Optimize F1-score",
        owner: str = "ml_scientist"
    ) -> ExperimentModel:
        """Create a new ML experiment container."""
        exp = ExperimentModel(
            tenant_id=tenant_id,
            name=name,
            description=description,
            objective=objective,
            owner=owner,
            status="ACTIVE",
        )
        session.add(exp)
        session.commit()
        session.refresh(exp)
        logger.info("Created Experiment id=%s name=%s tenant=%s", exp.id, name, tenant_id)
        return exp

    @staticmethod
    def log_run(
        session: Session,
        experiment_id: str,
        tenant_id: str,
        algorithm: str,
        hyperparameters: Dict[str, Any],
        parameters: Dict[str, Any],
        metrics: Dict[str, float],
        artifacts: Dict[str, Any],
        dataset_version: str = "1.0",
        feature_set_version: int = 1,
        status: str = "COMPLETED",
        failure_reason: Optional[str] = None
    ) -> ExperimentRunModel:
        """Log a reproducible experiment run with hyperparameters, seeds, and metrics."""
        run = ExperimentRunModel(
            experiment_id=experiment_id,
            tenant_id=tenant_id,
            dataset_version=dataset_version,
            feature_set_version=feature_set_version,
            algorithm=algorithm,
            hyperparameters_json=hyperparameters,
            parameters_json=parameters,
            metrics_json=metrics,
            artifacts_json=artifacts,
            status=status,
            failure_reason=failure_reason,
            training_started_at=datetime.now(timezone.utc),
            training_completed_at=datetime.now(timezone.utc) if status == "COMPLETED" else None,
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        logger.info("Logged ExperimentRun id=%s algorithm=%s status=%s tenant=%s", run.id, algorithm, status, tenant_id)
        return run
