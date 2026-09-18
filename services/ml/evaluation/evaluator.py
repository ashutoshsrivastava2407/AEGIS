"""AEGIS Formal Model Evaluator."""

from datetime import datetime, timezone
import logging
import math
from typing import Any, Dict, List, Optional
import numpy as np
from sqlalchemy.orm import Session
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, mean_squared_error, r2_score

from packages.database.models.ml_evaluation import ModelEvaluationModel

logger = logging.getLogger("aegis.ml.evaluation")


class ModelEvaluator:
    """Computes task-appropriate model metrics on test evaluation datasets."""

    @staticmethod
    def evaluate_model(
        session: Session,
        tenant_id: str,
        model_id: str,
        model_version: int,
        task_type: str,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        dataset_version: str = "1.0"
    ) -> ModelEvaluationModel:
        """Compute task-appropriate metrics and persist ModelEvaluationModel."""
        task_upper = task_type.upper()
        metrics: Dict[str, float] = {}

        if task_upper == "CLASSIFICATION":
            acc = float(accuracy_score(y_true, y_pred))
            prec = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
            rec = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
            f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

            metrics = {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
            }

        elif task_upper in ("REGRESSION", "FORECASTING"):
            mae = float(mean_absolute_error(y_true, y_pred))
            mse = float(mean_squared_error(y_true, y_pred))
            rmse = float(math.sqrt(mse))
            r2 = float(r2_score(y_true, y_pred)) if len(y_true) > 1 else 1.0

            metrics = {
                "mae": round(mae, 4),
                "mse": round(mse, 4),
                "rmse": round(rmse, 4),
                "r2_score": round(r2, 4),
            }

        elif task_upper == "ANOMALY_DETECTION":
            # Predictions -1 = anomaly, 1 = normal in IsolationForest
            anomalies_count = int(np.sum(y_pred == -1))
            total_count = len(y_pred)
            det_rate = float(anomalies_count / total_count) if total_count > 0 else 0.0

            metrics = {
                "anomalies_detected": anomalies_count,
                "total_samples": total_count,
                "detection_rate": round(det_rate, 4),
            }

        else:
            metrics = {"evaluation_samples": len(y_true)}

        evaluation = ModelEvaluationModel(
            tenant_id=tenant_id,
            model_id=model_id,
            model_version=model_version,
            dataset_version=dataset_version,
            metrics_json=metrics,
            evaluation_config_json={"task_type": task_upper, "samples": len(y_true)},
            evaluated_at=datetime.now(timezone.utc),
        )
        session.add(evaluation)
        session.commit()
        session.refresh(evaluation)
        logger.info("Evaluated Model id=%s v%d task=%s metrics=%s", model_id, model_version, task_upper, metrics)
        return evaluation
