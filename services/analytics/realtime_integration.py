"""AEGIS Real-Time Streaming Analytics Integration.

Aggregates real-time Silver event streams into metric state and triggers live anomaly evaluation.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from packages.events.envelope import EventEnvelope
from services.analytics.anomaly_detection import AnomalyDetector
from services.analytics.insight_engine import InsightEngine

logger = logging.getLogger("aegis.analytics.realtime_integration")


class RealTimeAnalyticsAggregator:
    """Aggregates real-time event streams into live analytical state."""

    def __init__(self):
        # Maps (tenant_id, topic_name) -> List[float]
        self._metric_windows: Dict[str, List[float]] = {}

    def process_realtime_event_batch(
        self,
        session: Session,
        tenant_id: str,
        topic_name: str,
        events: List[EventEnvelope]
    ) -> Dict[str, Any]:
        """Update streaming metric window and check for real-time anomalies."""
        if not events:
            return {"processed": 0, "anomalies_detected": 0}

        window_key = f"{tenant_id}:{topic_name}"
        if window_key not in self._metric_windows:
            self._metric_windows[window_key] = [10.0, 12.0, 11.5, 13.0, 12.8, 11.9, 12.2]

        current_value = float(len(events) * 10.0)  # Rate per batch
        history = self._metric_windows[window_key]

        # Evaluate anomaly
        anomaly = AnomalyDetector.evaluate(
            session=session,
            tenant_id=tenant_id,
            metric_id=f"streaming-metric-{topic_name}",
            current_value=current_value,
            history=history,
            method="Z_SCORE",
        )

        anomalies_count = 0
        if anomaly:
            anomalies_count = 1
            InsightEngine.generate_from_anomaly(session, tenant_id, anomaly)

        # Update rolling window
        history.append(current_value)
        if len(history) > 50:
            history.pop(0)

        return {
            "processed": len(events),
            "current_metric_value": current_value,
            "anomalies_detected": anomalies_count,
        }
