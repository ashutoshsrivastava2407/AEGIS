"""AEGIS Analytics & Intelligence Data Platform Application Service.

Unified application service orchestrating datasets, metric definitions, query execution, time-series analysis, statistical anomaly detection, trend direction, insight generation, and alert evaluations.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.analytical_dataset import AnalyticalDatasetModel
from packages.database.models.metric_definition import MetricDefinitionModel
from packages.database.models.query_execution import QueryExecutionModel, SavedQueryModel
from packages.database.models.dashboard import DashboardModel, DashboardWidgetModel
from packages.database.models.anomaly import AnomalyModel
from packages.database.models.insight import InsightModel
from packages.database.models.alert import AlertRuleModel, AlertEventModel

from services.analytics.datasets import AnalyticalDatasetRegistry
from services.analytics.metrics import MetricEngine
from services.analytics.query_engine import AnalyticalQueryEngine
from services.analytics.time_series import TimeSeriesAnalyzer
from services.analytics.anomaly_detection import AnomalyDetector
from services.analytics.trend_detection import TrendDetector
from services.analytics.insight_engine import InsightEngine
from services.analytics.alert_evaluator import AlertEvaluator

logger = logging.getLogger("aegis.analytics.service")


class AnalyticsDataPlatformService:
    """Unified application service facade for Analytics & Intelligence."""

    def __init__(self):
        self.query_engine = AnalyticalQueryEngine()

    def get_overview(self, tenant_id: str, db: Session) -> Dict[str, Any]:
        """Fetch analytics platform executive operational summary."""
        total_datasets = db.query(AnalyticalDatasetModel).filter(AnalyticalDatasetModel.tenant_id == tenant_id).count()
        total_metrics = db.query(MetricDefinitionModel).filter(MetricDefinitionModel.tenant_id == tenant_id).count()
        active_anomalies = db.query(AnomalyModel).filter(AnomalyModel.tenant_id == tenant_id, AnomalyModel.status == "ACTIVE").count()
        open_insights = db.query(InsightModel).filter(InsightModel.tenant_id == tenant_id, InsightModel.status == "OPEN").count()
        active_alerts = db.query(AlertEventModel).filter(AlertEventModel.tenant_id == tenant_id, AlertEventModel.status == "OPEN").count()
        total_queries = db.query(QueryExecutionModel).filter(QueryExecutionModel.tenant_id == tenant_id).count()

        return {
            "status": "OPERATIONAL",
            "total_analytical_datasets": total_datasets,
            "total_metrics": total_metrics,
            "active_anomalies": active_anomalies,
            "open_insights": open_insights,
            "active_alerts": active_alerts,
            "total_queries_executed": total_queries,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Analytical Datasets
    def list_datasets(self, tenant_id: str, db: Session) -> List[Dict[str, Any]]:
        datasets = db.query(AnalyticalDatasetModel).filter(AnalyticalDatasetModel.tenant_id == tenant_id).all()
        return [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "source_dataset_id": d.source_dataset_id,
                "source_layer": d.source_layer,
                "version": d.version,
                "schema_json": d.schema_json,
                "owner": d.owner,
                "status": d.status,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in datasets
        ]

    def create_dataset(self, tenant_id: str, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        ds = AnalyticalDatasetRegistry.register_dataset(
            session=db,
            tenant_id=tenant_id,
            name=data["name"],
            description=data.get("description"),
            source_dataset_id=data.get("source_dataset_id"),
            source_layer=data.get("source_layer", "GOLD"),
            schema_json=data.get("schema_json"),
            owner=data.get("owner", "analytics_team"),
        )
        return {"id": ds.id, "name": ds.name, "status": ds.status}

    # Metric Definitions
    def list_metrics(self, tenant_id: str, db: Session) -> List[Dict[str, Any]]:
        metrics = db.query(MetricDefinitionModel).filter(MetricDefinitionModel.tenant_id == tenant_id).all()
        return [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "owner": m.owner,
                "unit": m.unit,
                "aggregation_type": m.aggregation_type,
                "dimensions": m.dimensions,
                "time_grain": m.time_grain,
                "calculation_formula": m.calculation_formula,
                "version": m.version,
                "status": m.status,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in metrics
        ]

    def create_metric(self, tenant_id: str, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        m = MetricEngine.create_metric(
            session=db,
            tenant_id=tenant_id,
            name=data["name"],
            description=data.get("description"),
            unit=data.get("unit", "COUNT"),
            aggregation_type=data.get("aggregation_type", "SUM"),
            dimensions=data.get("dimensions", []),
            time_grain=data.get("time_grain", "DAILY"),
            source_dataset_id=data.get("source_dataset_id"),
            calculation_formula=data.get("calculation_formula", "SUM(value)"),
        )
        return {"id": m.id, "name": m.name, "version": m.version}

    def evaluate_metric(self, tenant_id: str, metric_id: str, db: Session, history_series: Optional[List[float]] = None) -> Dict[str, Any]:
        metric = db.query(MetricDefinitionModel).filter(MetricDefinitionModel.id == metric_id, MetricDefinitionModel.tenant_id == tenant_id).first()
        if not metric:
            raise ValueError(f"Metric id '{metric_id}' not found for tenant '{tenant_id}'")

        series = history_series or [105.0, 110.2, 108.4, 112.0, 115.5, 114.0, 158.0]  # Intentional outlier 158.0 at end
        current_val = series[-1]

        calc_val = MetricEngine.calculate(metric, series)
        trend = TrendDetector.analyze_trend(series)

        # Trigger anomaly scan
        anomaly = AnomalyDetector.evaluate(
            session=db,
            tenant_id=tenant_id,
            metric_id=metric.id,
            current_value=current_val,
            history=series[:-1],
            method="Z_SCORE",
        )

        insight_created = None
        if anomaly:
            insight_created = InsightEngine.generate_from_anomaly(db, tenant_id, anomaly, metric)

        # Evaluate active alert rules
        rules = db.query(AlertRuleModel).filter(AlertRuleModel.tenant_id == tenant_id, AlertRuleModel.metric_id == metric_id).all()
        alert_fired = None
        for r in rules:
            evt = AlertEvaluator.evaluate_rule(db, r, current_val, recent_anomaly=anomaly)
            if evt:
                alert_fired = evt.id

        return {
            "metric_id": metric.id,
            "metric_name": metric.name,
            "value": calc_val,
            "trend": trend.to_dict(),
            "anomaly_detected": anomaly is not None,
            "anomaly_id": anomaly.id if anomaly else None,
            "insight_id": insight_created.id if insight_created else None,
            "alert_fired": alert_fired is not None,
        }

    # Query Execution & Saved Queries
    def execute_analytical_query(
        self,
        tenant_id: str,
        sql_text: str,
        parameters: Optional[Dict[str, Any]],
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        return self.query_engine.execute_query(
            session=db,
            tenant_id=tenant_id,
            sql_text=sql_text,
            parameters=parameters,
            user_id=user_id,
        )

    def list_query_history(self, tenant_id: str, db: Session) -> List[Dict[str, Any]]:
        history = db.query(QueryExecutionModel).filter(QueryExecutionModel.tenant_id == tenant_id).order_by(QueryExecutionModel.created_at.desc()).limit(100).all()
        return [
            {
                "id": h.id,
                "user_id": h.user_id,
                "sql_text": h.sql_text,
                "duration_ms": h.duration_ms,
                "status": h.status,
                "row_count": h.row_count,
                "error_message": h.error_message,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in history
        ]

    def list_saved_queries(self, tenant_id: str, db: Session) -> List[Dict[str, Any]]:
        queries = db.query(SavedQueryModel).filter(SavedQueryModel.tenant_id == tenant_id).all()
        return [
            {
                "id": q.id,
                "name": q.name,
                "description": q.description,
                "sql_text": q.sql_text,
                "owner": q.owner,
                "tags": q.tags,
                "created_at": q.created_at.isoformat() if q.created_at else None,
            }
            for q in queries
        ]

    def create_saved_query(self, tenant_id: str, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        sq = SavedQueryModel(
            tenant_id=tenant_id,
            name=data["name"],
            description=data.get("description"),
            sql_text=data["sql_text"],
            parameters_json=data.get("parameters", {}),
            owner=data.get("owner", "analytics_user"),
            tags=data.get("tags", []),
        )
        db.add(sq)
        db.commit()
        db.refresh(sq)
        return {"id": sq.id, "name": sq.name}

    # Dashboards
    def list_dashboards(self, tenant_id: str, db: Session) -> List[Dict[str, Any]]:
        dashboards = db.query(DashboardModel).filter(DashboardModel.tenant_id == tenant_id).all()
        res = []
        for d in dashboards:
            widgets = db.query(DashboardWidgetModel).filter(DashboardWidgetModel.dashboard_id == d.id).all()
            res.append({
                "id": d.id,
                "title": d.title,
                "description": d.description,
                "owner": d.owner,
                "widgets_count": len(widgets),
                "created_at": d.created_at.isoformat() if d.created_at else None,
            })
        return res

    def create_dashboard(self, tenant_id: str, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        dashboard = DashboardModel(
            tenant_id=tenant_id,
            title=data["title"],
            description=data.get("description"),
            owner=data.get("owner", "analytics_admin"),
        )
        db.add(dashboard)
        db.commit()
        db.refresh(dashboard)
        return {"id": dashboard.id, "title": dashboard.title}

    # Anomalies, Insights & Alerts
    def list_anomalies(self, tenant_id: str, db: Session) -> List[Dict[str, Any]]:
        anomalies = db.query(AnomalyModel).filter(AnomalyModel.tenant_id == tenant_id).order_by(AnomalyModel.detected_at.desc()).limit(100).all()
        return [
            {
                "id": a.id,
                "metric_id": a.metric_id,
                "observed_value": a.observed_value,
                "expected_value": a.expected_value,
                "expected_min": a.expected_min,
                "expected_max": a.expected_max,
                "z_score": a.z_score,
                "severity": a.severity,
                "detection_method": a.detection_method,
                "status": a.status,
                "evidence_json": a.evidence_json,
                "detected_at": a.detected_at.isoformat() if a.detected_at else None,
            }
            for a in anomalies
        ]

    def list_insights(self, tenant_id: str, db: Session) -> List[Dict[str, Any]]:
        insights = db.query(InsightModel).filter(InsightModel.tenant_id == tenant_id).order_by(InsightModel.created_at.desc()).limit(100).all()
        return [
            {
                "id": i.id,
                "insight_type": i.insight_type,
                "title": i.title,
                "description": i.description,
                "metric_id": i.metric_id,
                "severity": i.severity,
                "evidence_json": i.evidence_json,
                "status": i.status,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in insights
        ]

    def list_alert_rules(self, tenant_id: str, db: Session) -> List[Dict[str, Any]]:
        rules = db.query(AlertRuleModel).filter(AlertRuleModel.tenant_id == tenant_id).all()
        return [
            {
                "id": r.id,
                "metric_id": r.metric_id,
                "name": r.name,
                "description": r.description,
                "condition_type": r.condition_type,
                "threshold_value": r.threshold_value,
                "severity": r.severity,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rules
        ]

    def create_alert_rule(self, tenant_id: str, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        rule = AlertRuleModel(
            tenant_id=tenant_id,
            metric_id=data["metric_id"],
            name=data["name"],
            description=data.get("description"),
            condition_type=data.get("condition_type", "THRESHOLD_GREATER"),
            threshold_value=data.get("threshold_value", 0.0),
            severity=data.get("severity", "HIGH"),
            status="ACTIVE",
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return {"id": rule.id, "name": rule.name}

    def list_alert_events(self, tenant_id: str, db: Session) -> List[Dict[str, Any]]:
        events = db.query(AlertEventModel).filter(AlertEventModel.tenant_id == tenant_id).order_by(AlertEventModel.triggered_at.desc()).limit(100).all()
        return [
            {
                "id": e.id,
                "rule_id": e.rule_id,
                "metric_id": e.metric_id,
                "triggered_value": e.triggered_value,
                "threshold_value": e.threshold_value,
                "severity": e.severity,
                "status": e.status,
                "triggered_at": e.triggered_at.isoformat() if e.triggered_at else None,
            }
            for e in events
        ]


# Global singleton instance
analytics_service = AnalyticsDataPlatformService()
