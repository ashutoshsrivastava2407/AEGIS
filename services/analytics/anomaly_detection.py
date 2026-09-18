"""AEGIS Statistical Anomaly Detector Engine.

Provides an extensible strategy framework for statistical outlier detection:
- ZScoreStrategy: z = (x - mu) / sigma (with zero variance protection)
- EWMAStrategy: Exponentially weighted moving average deviation
- RollingThresholdStrategy: Min/Max boundary evaluation
- SeasonalBaselineStrategy: Historical baseline comparison
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from packages.database.models.anomaly import AnomalyModel

logger = logging.getLogger("aegis.analytics.anomaly")


class AnomalyDetectionResult:
    def __init__(
        self,
        is_anomaly: bool,
        score: float,
        z_score: float,
        observed_value: float,
        expected_value: float,
        expected_min: float,
        expected_max: float,
        severity: str,
        detection_method: str,
        evidence: Dict[str, Any]
    ):
        self.is_anomaly = is_anomaly
        self.score = score
        self.z_score = z_score
        self.observed_value = observed_value
        self.expected_value = expected_value
        self.expected_min = expected_min
        self.expected_max = expected_max
        self.severity = severity
        self.detection_method = detection_method
        self.evidence = evidence


class BaseAnomalyStrategy(ABC):
    """Abstract Strategy interface for Anomaly Detection algorithms."""

    @abstractmethod
    def detect(self, current_value: float, history: List[float], **kwargs) -> AnomalyDetectionResult:
        pass


class ZScoreStrategy(BaseAnomalyStrategy):
    """Statistical Z-Score Anomaly Detection Strategy.
    
    Formula: z = (x - mu) / sigma
    Handles zero variance protection safely.
    """

    def __init__(self, z_threshold: float = 2.5):
        self.z_threshold = z_threshold

    def detect(self, current_value: float, history: List[float], **kwargs) -> AnomalyDetectionResult:
        if not history:
            return AnomalyDetectionResult(
                is_anomaly=False, score=0.0, z_score=0.0, observed_value=current_value,
                expected_value=current_value, expected_min=current_value, expected_max=current_value,
                severity="LOW", detection_method="Z_SCORE", evidence={"reason": "Insufficient history"}
            )

        n = len(history)
        mu = sum(history) / float(n)
        variance = sum((x - mu) ** 2 for x in history) / float(n)
        sigma = math.sqrt(variance)

        # Division by zero safeguard
        if sigma == 0.0 or math.isnan(sigma):
            is_anomaly = abs(current_value - mu) > 0.0001
            z = 999.0 if is_anomaly else 0.0
        else:
            z = (current_value - mu) / sigma
            is_anomaly = abs(z) >= self.z_threshold

        abs_z = abs(z)

        # Severity classification based on z-score magnitude
        if abs_z >= 4.0:
            severity = "CRITICAL"
        elif abs_z >= 3.0:
            severity = "HIGH"
        elif abs_z >= 2.5:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        expected_min = mu - (self.z_threshold * sigma)
        expected_max = mu + (self.z_threshold * sigma)

        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            score=round(abs_z, 2),
            z_score=round(z, 2),
            observed_value=round(current_value, 4),
            expected_value=round(mu, 4),
            expected_min=round(expected_min, 4),
            expected_max=round(expected_max, 4),
            severity=severity,
            detection_method="Z_SCORE",
            evidence={
                "mean": round(mu, 4),
                "std_dev": round(sigma, 4),
                "sample_size": n,
                "z_score_raw": z,
            }
        )


class RollingThresholdStrategy(BaseAnomalyStrategy):
    """Min/Max Bound Anomaly Detection Strategy."""

    def __init__(self, min_bound: Optional[float] = None, max_bound: Optional[float] = None):
        self.min_bound = min_bound
        self.max_bound = max_bound

    def detect(self, current_value: float, history: List[float], **kwargs) -> AnomalyDetectionResult:
        min_b = kwargs.get("min_bound", self.min_bound)
        max_b = kwargs.get("max_bound", self.max_bound)

        is_below = min_b is not None and current_value < min_b
        is_above = max_b is not None and current_value > max_b
        is_anomaly = is_below or is_above

        severity = "HIGH" if is_anomaly else "LOW"

        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            score=1.0 if is_anomaly else 0.0,
            z_score=0.0,
            observed_value=current_value,
            expected_value=(min_b + max_b) / 2.0 if (min_b and max_b) else current_value,
            expected_min=min_b if min_b is not None else current_value,
            expected_max=max_b if max_b is not None else current_value,
            severity=severity,
            detection_method="ROLLING_THRESHOLD",
            evidence={"min_bound": min_b, "max_bound": max_b}
        )


class EWMADetector(BaseAnomalyStrategy):
    """Exponentially Weighted Moving Average Strategy."""

    def __init__(self, alpha: float = 0.3, threshold_mult: float = 2.5):
        self.alpha = alpha
        self.threshold_mult = threshold_mult

    def detect(self, current_value: float, history: List[float], **kwargs) -> AnomalyDetectionResult:
        if not history:
            return ZScoreStrategy().detect(current_value, history)

        ewma = history[0]
        for val in history[1:]:
            ewma = self.alpha * val + (1 - self.alpha) * ewma

        dev = abs(current_value - ewma)
        avg_dev = sum(abs(x - ewma) for x in history) / len(history)
        is_anomaly = dev > (self.threshold_mult * avg_dev) if avg_dev > 0 else False

        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            score=round(dev / avg_dev, 2) if avg_dev > 0 else 0.0,
            z_score=0.0,
            observed_value=current_value,
            expected_value=round(ewma, 4),
            expected_min=round(ewma - self.threshold_mult * avg_dev, 4),
            expected_max=round(ewma + self.threshold_mult * avg_dev, 4),
            severity="HIGH" if is_anomaly else "LOW",
            detection_method="EWMA",
            evidence={"ewma": round(ewma, 4), "avg_dev": round(avg_dev, 4)}
        )


class AnomalyDetector:
    """Orchestrator for statistical anomaly detection across metric time-series."""

    STRATEGIES: Dict[str, BaseAnomalyStrategy] = {
        "Z_SCORE": ZScoreStrategy(),
        "EWMA": EWMADetector(),
        "ROLLING_THRESHOLD": RollingThresholdStrategy(),
    }

    @classmethod
    def evaluate(
        cls,
        session: Session,
        tenant_id: str,
        metric_id: str,
        current_value: float,
        history: List[float],
        method: str = "Z_SCORE",
        dataset_id: Optional[str] = None,
        **kwargs
    ) -> Optional[AnomalyModel]:
        """Evaluate current metric value against historical window and persist AnomalyModel if breached."""
        strategy = cls.STRATEGIES.get(method.upper(), ZScoreStrategy())
        result = strategy.detect(current_value, history, **kwargs)

        if not result.is_anomaly:
            return None

        record = AnomalyModel(
            tenant_id=tenant_id,
            metric_id=metric_id,
            dataset_id=dataset_id,
            observed_value=result.observed_value,
            expected_value=result.expected_value,
            expected_min=result.expected_min,
            expected_max=result.expected_max,
            z_score=result.z_score,
            severity=result.severity,
            detection_method=result.detection_method,
            status="ACTIVE",
            evidence_json=result.evidence,
            lineage_ref=f"metric:{metric_id}",
        )
        session.add(record)
        session.commit()
        session.refresh(record)

        logger.warning(
            "Detected Anomaly id=%s tenant=%s metric=%s z_score=%.2f severity=%s",
            record.id, tenant_id, metric_id, result.z_score, result.severity
        )
        return record
