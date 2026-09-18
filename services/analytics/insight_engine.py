"""AEGIS Factual Insight Engine.

Generates structured analytical insights and dimensional contribution breakdowns backed by empirical data.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.insight import InsightModel
from packages.database.models.anomaly import AnomalyModel
from packages.database.models.metric_definition import MetricDefinitionModel

logger = logging.getLogger("aegis.analytics.insight")


class InsightEngine:
    """Factual Analytical Insight Generator."""

    @staticmethod
    def generate_from_anomaly(
        session: Session,
        tenant_id: str,
        anomaly: AnomalyModel,
        metric: Optional[MetricDefinitionModel] = None
    ) -> InsightModel:
        """Create a factual insight from a detected statistical anomaly."""
        metric_name = metric.name if metric else "Governed Metric"
        pct_dev = round(((anomaly.observed_value - anomaly.expected_value) / abs(anomaly.expected_value)) * 100.0, 1) if anomaly.expected_value != 0 else 0.0

        title = f"Statistical Anomaly Detected on {metric_name}"
        desc = (
            f"Observed value ({anomaly.observed_value}) deviated by {pct_dev}% from expected value "
            f"({anomaly.expected_value}) with z-score of {anomaly.z_score:.2f}."
        )

        insight = InsightModel(
            tenant_id=tenant_id,
            insight_type="ANOMALY_BREAKDOWN",
            title=title,
            description=desc,
            metric_id=anomaly.metric_id,
            dataset_id=anomaly.dataset_id,
            severity=anomaly.severity,
            evidence_json={
                "anomaly_id": anomaly.id,
                "observed_value": anomaly.observed_value,
                "expected_value": anomaly.expected_value,
                "z_score": anomaly.z_score,
                "detection_method": anomaly.detection_method,
            },
            lineage_ref=anomaly.lineage_ref,
            status="OPEN",
        )
        session.add(insight)
        session.commit()
        session.refresh(insight)
        logger.info("Generated Insight id=%s for anomaly=%s", insight.id, anomaly.id)
        return insight

    @staticmethod
    def generate_dimensional_contribution(
        session: Session,
        tenant_id: str,
        metric_id: str,
        dimension_name: str,
        breakdown: Dict[str, float]
    ) -> InsightModel:
        """Decompose metric changes by dimension contribution."""
        total = sum(breakdown.values()) if breakdown else 1.0
        sorted_items = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        top_contrib = sorted_items[0] if sorted_items else ("N/A", 0.0)
        top_pct = round((top_contrib[1] / total) * 100.0, 1) if total != 0 else 0.0

        title = f"Dimensional Contribution Driver: {dimension_name} ({top_contrib[0]})"
        desc = f"Top dimension '{top_contrib[0]}' represents {top_pct}% of total {dimension_name} metric distribution."

        insight = InsightModel(
            tenant_id=tenant_id,
            insight_type="CROSS_DIMENSION_CONTRIBUTION",
            title=title,
            description=desc,
            metric_id=metric_id,
            severity="INFO",
            evidence_json={
                "dimension_name": dimension_name,
                "top_contributor": top_contrib[0],
                "top_value": top_contrib[1],
                "contribution_pct": top_pct,
                "full_breakdown": breakdown,
            },
            status="OPEN",
        )
        session.add(insight)
        session.commit()
        session.refresh(insight)
        return insight
