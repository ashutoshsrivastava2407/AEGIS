"""AEGIS Stream Quality Evaluator.

Computes micro-batch and streaming window quality metrics, health scores, and anomaly indicators.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from packages.database.models.stream_quality import StreamQualityMetricsModel

logger = logging.getLogger("aegis.streaming.quality")


class StreamQualityEvaluator:
    """Evaluates streaming data quality dimensions and calculates streaming health score."""

    @staticmethod
    def evaluate_window(
        session: Session,
        tenant_id: str,
        topic_name: str,
        window_start: datetime,
        window_end: datetime,
        total_events: int,
        valid_events: int,
        invalid_schema_events: int,
        duplicate_events: int,
        late_events: int,
        avg_latency_ms: float = 0.0,
        extra_details: Optional[Dict[str, Any]] = None
    ) -> StreamQualityMetricsModel:
        """Calculate streaming quality metrics and health score for a window."""
        if total_events > 0:
            invalid_rate = invalid_schema_events / total_events
            duplicate_rate = duplicate_events / total_events
            late_rate = late_events / total_events

            # Health Score formula (0.0 to 100.0%)
            penalty = (invalid_rate * 40.0) + (duplicate_rate * 30.0) + (late_rate * 30.0)
            quality_score = max(0.0, min(100.0, 100.0 - penalty * 100.0))
        else:
            quality_score = 100.0

        metrics_record = StreamQualityMetricsModel(
            tenant_id=tenant_id,
            topic_name=topic_name,
            window_start=window_start,
            window_end=window_end,
            total_events=total_events,
            valid_events=valid_events,
            invalid_schema_events=invalid_schema_events,
            duplicate_events=duplicate_events,
            late_events=late_events,
            avg_latency_ms=avg_latency_ms,
            quality_score=round(quality_score, 2),
            details_json=extra_details or {},
        )

        session.add(metrics_record)
        session.commit()
        session.refresh(metrics_record)

        logger.info(
            "Stream quality evaluated tenant=%s topic=%s score=%.2f%% total=%d valid=%d invalid=%d",
            tenant_id, topic_name, metrics_record.quality_score, total_events, valid_events, invalid_schema_events
        )

        return metrics_record
