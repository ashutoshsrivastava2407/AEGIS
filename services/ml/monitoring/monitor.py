"""AEGIS Model & Prediction Monitoring Engine."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from packages.database.models.ml_inference import ModelInferenceLogModel
from packages.database.models.ml_deployment import ModelDeploymentModel

logger = logging.getLogger("aegis.ml.monitoring")


class ModelMonitor:
    """Aggregates inference performance metrics, prediction volume, and latency statistics."""

    @staticmethod
    def get_model_monitoring_stats(session: Session, tenant_id: str, model_version_id: Optional[str] = None) -> Dict[str, Any]:
        """Compute real inference volume, avg latency, failure rate, and status."""
        query = session.query(ModelInferenceLogModel).filter(ModelInferenceLogModel.tenant_id == tenant_id)
        if model_version_id:
            query = query.filter(ModelInferenceLogModel.model_version_id == model_version_id)

        logs = query.all()

        if not logs:
            return {
                "total_predictions": 0,
                "average_latency_ms": 0.0,
                "success_count": 0,
                "failure_count": 0,
                "failure_rate_pct": 0.0,
                "status": "HEALTHY",
            }

        total = len(logs)
        successes = sum(1 for l in logs if l.status == "SUCCESS")
        failures = total - successes
        avg_latency = float(sum(l.latency_ms for l in logs) / total)
        fail_rate = round(float(failures / total) * 100.0, 2)

        return {
            "total_predictions": total,
            "average_latency_ms": round(avg_latency, 2),
            "success_count": successes,
            "failure_count": failures,
            "failure_rate_pct": fail_rate,
            "status": "DEGRADED" if fail_rate > 5.0 else "HEALTHY",
        }
