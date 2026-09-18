"""AEGIS Governed Metric Engine.

Registers, evaluates, and versions KPI and metric definitions across datasets.
"""

from datetime import datetime, timezone
import logging
import math
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.metric_definition import MetricDefinitionModel

logger = logging.getLogger("aegis.analytics.metrics")


class MetricEngine:
    """Evaluates governed metric calculation definitions."""

    @staticmethod
    def create_metric(
        session: Session,
        tenant_id: str,
        name: str,
        description: Optional[str],
        unit: str,
        aggregation_type: str,
        dimensions: List[str],
        time_grain: str,
        source_dataset_id: Optional[str],
        calculation_formula: str,
        owner: str = "analytics_lead"
    ) -> MetricDefinitionModel:
        """Register a new governed metric definition."""
        metric = MetricDefinitionModel(
            tenant_id=tenant_id,
            name=name,
            description=description,
            unit=unit,
            aggregation_type=aggregation_type.upper(),
            dimensions=dimensions or [],
            time_grain=time_grain.upper(),
            source_dataset_id=source_dataset_id,
            calculation_formula=calculation_formula,
            owner=owner,
            version=1,
            status="ACTIVE",
        )
        session.add(metric)
        session.commit()
        session.refresh(metric)
        logger.info("Registered MetricDefinition id=%s name=%s tenant=%s", metric.id, name, tenant_id)
        return metric

    @staticmethod
    def calculate(
        metric: MetricDefinitionModel,
        values: List[float]
    ) -> float:
        """Execute calculation rule over dataset values."""
        if not values:
            return 0.0

        agg = metric.aggregation_type.upper()
        if agg == "SUM":
            return float(sum(values))
        elif agg == "AVG":
            return float(sum(values) / len(values))
        elif agg == "COUNT":
            return float(len(values))
        elif agg == "MIN":
            return float(min(values))
        elif agg == "MAX":
            return float(max(values))
        elif agg == "FORMULA":
            # Simple formula evaluation e.g. SUM or RATIO
            return float(sum(values))
        else:
            return float(sum(values))
