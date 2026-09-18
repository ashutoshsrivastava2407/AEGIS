"""AEGIS Statistical Feature & Model Drift Detection Engine."""

from datetime import datetime, timezone
import logging
import math
from typing import Dict, Any, List, Optional
import numpy as np
from sqlalchemy.orm import Session

from packages.database.models.ml_drift import ModelDriftRecordModel

logger = logging.getLogger("aegis.ml.drift")


class DriftDetectionResult:
    def __init__(self, status: str, score: float, threshold: float, evidence: Dict[str, Any]):
        self.status = status  # NO_DRIFT, DRIFT_DETECTED, INSUFFICIENT_DATA
        self.score = score
        self.threshold = threshold
        self.evidence = evidence


class DriftDetector:
    """Computes Population Stability Index (PSI) and distribution shift."""

    @staticmethod
    def calculate_psi(reference: np.ndarray, current: np.ndarray, num_buckets: int = 5) -> float:
        """Calculate Population Stability Index (PSI) between reference and current feature distributions."""
        if len(reference) == 0 or len(current) == 0:
            return 0.0

        min_val = min(np.min(reference), np.min(current))
        max_val = max(np.max(reference), np.max(current))

        if min_val == max_val:
            return 0.0

        buckets = np.linspace(min_val, max_val, num_buckets + 1)
        ref_counts, _ = np.histogram(reference, bins=buckets)
        cur_counts, _ = np.histogram(current, bins=buckets)

        ref_pct = ref_counts / float(len(reference))
        cur_pct = cur_counts / float(len(current))

        # Safeguard epsilon to prevent division by zero or log(0)
        eps = 1e-4
        ref_pct = np.where(ref_pct == 0, eps, ref_pct)
        cur_pct = np.where(cur_pct == 0, eps, cur_pct)

        psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
        return round(float(psi), 4)

    @classmethod
    def evaluate_feature_drift(
        cls,
        session: Session,
        tenant_id: str,
        model_id: str,
        feature_name: str,
        reference_data: List[float],
        current_data: List[float],
        threshold: float = 0.1
    ) -> ModelDriftRecordModel:
        """Evaluate drift over feature samples and persist ModelDriftRecordModel."""
        if len(reference_data) < 2 or len(current_data) < 2:
            status = "INSUFFICIENT_DATA"
            score = 0.0
            evidence = {"reason": "Insufficient sample points for drift computation"}
        else:
            ref_arr = np.array(reference_data)
            cur_arr = np.array(current_data)
            score = cls.calculate_psi(ref_arr, cur_arr)
            status = "DRIFT_DETECTED" if score >= threshold else "NO_DRIFT"
            evidence = {
                "reference_mean": round(float(np.mean(ref_arr)), 4),
                "current_mean": round(float(np.mean(cur_arr)), 4),
                "reference_std": round(float(np.std(ref_arr)), 4),
                "current_std": round(float(np.std(cur_arr)), 4),
                "reference_size": len(reference_data),
                "current_size": len(current_data),
            }

        drift_record = ModelDriftRecordModel(
            tenant_id=tenant_id,
            model_id=model_id,
            feature_name=feature_name,
            reference_period="BASELINE_TRAINING",
            current_period="RECENT_INFERENCE_30D",
            method="POPULATION_STABILITY_INDEX",
            score=score,
            threshold=threshold,
            status=status,
            evidence_json=evidence,
            detected_at=datetime.now(timezone.utc),
        )
        session.add(drift_record)
        session.commit()
        session.refresh(drift_record)

        if status == "DRIFT_DETECTED":
            logger.warning("Feature Drift Detected! model=%s feature=%s PSI=%.4f threshold=%.2f", model_id, feature_name, score, threshold)
        return drift_record
