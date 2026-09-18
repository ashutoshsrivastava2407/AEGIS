"""AEGIS Alert Rule Condition Evaluator.

Evaluates governed metric rules, threshold breaches, and anomaly detections, triggering AlertEventModel records.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.alert import AlertRuleModel, AlertEventModel
from packages.database.models.anomaly import AnomalyModel

logger = logging.getLogger("aegis.analytics.alert")


class AlertEvaluator:
    """Evaluates alert conditions and fires alert events."""

    @staticmethod
    def evaluate_rule(
        session: Session,
        rule: AlertRuleModel,
        current_value: float,
        recent_anomaly: Optional[AnomalyModel] = None
    ) -> Optional[AlertEventModel]:
        """Evaluate single alert rule against current metric value or anomaly."""
        if rule.status != "ACTIVE":
            return None

        triggered = False
        cond = rule.condition_type.upper()

        if cond == "THRESHOLD_GREATER" and current_value > rule.threshold_value:
            triggered = True
        elif cond == "THRESHOLD_LESS" and current_value < rule.threshold_value:
            triggered = True
        elif cond == "ANOMALY_DETECTED" and recent_anomaly is not None:
            triggered = True

        if not triggered:
            return None

        alert_event = AlertEventModel(
            tenant_id=rule.tenant_id,
            rule_id=rule.id,
            metric_id=rule.metric_id,
            triggered_value=current_value,
            threshold_value=rule.threshold_value,
            severity=rule.severity,
            status="OPEN",
            details_json={
                "rule_name": rule.name,
                "condition_type": cond,
                "triggered_at": datetime.now(timezone.utc).isoformat(),
                "anomaly_id": recent_anomaly.id if recent_anomaly else None,
            },
        )
        session.add(alert_event)
        session.commit()
        session.refresh(alert_event)

        logger.warning(
            "Alert Triggered rule_id=%s tenant=%s metric=%s val=%.2f threshold=%.2f",
            rule.id, rule.tenant_id, rule.metric_id, current_value, rule.threshold_value
        )
        return alert_event
