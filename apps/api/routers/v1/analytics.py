"""AEGIS Analytics & Intelligence Platform REST API Router.

Exposes endpoints for analytical datasets, metrics, AST-guarded queries, dashboards, anomalies, insights, and alerts.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from packages.database.session import get_db
from services.analytics.services import AnalyticsDataPlatformService, analytics_service
from services.analytics.query_engine import SQLSecurityValidationError

router = APIRouter(prefix="/analytics", tags=["analytics"])

DEFAULT_TENANT_ID = "tenant-aegis-primary"


@router.get("/overview")
def get_analytics_overview(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve Analytics Platform executive overview and status."""
    return analytics_service.get_overview(tenant_id, db)


# Datasets
@router.get("/datasets")
def list_analytical_datasets(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List registered analytical datasets."""
    datasets = analytics_service.list_datasets(tenant_id, db)
    return {"datasets": datasets, "total": len(datasets)}


@router.post("/datasets", status_code=status.HTTP_201_CREATED)
def create_analytical_dataset(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Register a new governed analytical dataset."""
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Dataset name is required.")
    return analytics_service.create_dataset(tenant_id, data, db)


# Metrics
@router.get("/metrics")
def list_metric_definitions(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List governed KPI and metric definitions."""
    metrics = analytics_service.list_metrics(tenant_id, db)
    return {"metrics": metrics, "total": len(metrics)}


@router.post("/metrics", status_code=status.HTTP_201_CREATED)
def create_metric_definition(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a new governed metric definition."""
    if not data.get("name") or not data.get("calculation_formula"):
        raise HTTPException(status_code=400, detail="Fields 'name' and 'calculation_formula' are required.")
    return analytics_service.create_metric(tenant_id, data, db)


@router.post("/metrics/{metric_id}/evaluate")
def evaluate_metric(
    metric_id: str,
    payload: Optional[Dict[str, Any]] = None,
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Calculate metric value, trend direction, and check for anomalies."""
    history = payload.get("history") if payload else None
    try:
        return analytics_service.evaluate_metric(tenant_id, metric_id, db, history_series=history)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


# Query Execution & Saved Queries
@router.post("/query")
def execute_analytical_query(
    body: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Execute AST-guarded read-only SELECT analytical query."""
    sql_text = body.get("sql_text")
    if not sql_text:
        raise HTTPException(status_code=400, detail="Field 'sql_text' is required.")

    params = body.get("parameters", {})
    user_id = body.get("user_id", "analytics_user")

    try:
        return analytics_service.execute_analytical_query(tenant_id, sql_text, params, user_id, db)
    except SQLSecurityValidationError as se:
        raise HTTPException(status_code=403, detail=f"SQL Security Guard Error: {str(se)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query Execution Error: {str(e)}")


@router.get("/queries")
def list_query_history(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List analytical query execution history logs."""
    history = analytics_service.list_query_history(tenant_id, db)
    return {"query_history": history, "total": len(history)}


@router.get("/saved-queries")
def list_saved_queries(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List saved analytical query views."""
    queries = analytics_service.list_saved_queries(tenant_id, db)
    return {"saved_queries": queries, "total": len(queries)}


@router.post("/saved-queries", status_code=status.HTTP_201_CREATED)
def create_saved_query(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Save an analytical query view."""
    if not data.get("name") or not data.get("sql_text"):
        raise HTTPException(status_code=400, detail="Fields 'name' and 'sql_text' are required.")
    return analytics_service.create_saved_query(tenant_id, data, db)


# Dashboards
@router.get("/dashboards")
def list_dashboards(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List metric dashboards."""
    dashboards = analytics_service.list_dashboards(tenant_id, db)
    return {"dashboards": dashboards, "total": len(dashboards)}


@router.post("/dashboards", status_code=status.HTTP_201_CREATED)
def create_dashboard(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a new metric dashboard layout."""
    if not data.get("title"):
        raise HTTPException(status_code=400, detail="Dashboard 'title' is required.")
    return analytics_service.create_dashboard(tenant_id, data, db)


# Anomalies, Insights & Alerts
@router.get("/anomalies")
def list_anomalies(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List statistical anomalies."""
    anomalies = analytics_service.list_anomalies(tenant_id, db)
    return {"anomalies": anomalies, "total": len(anomalies)}


@router.get("/insights")
def list_insights(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List factual analytical insights."""
    insights = analytics_service.list_insights(tenant_id, db)
    return {"insights": insights, "total": len(insights)}


@router.get("/alerts/rules")
def list_alert_rules(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List alert rules."""
    rules = analytics_service.list_alert_rules(tenant_id, db)
    return {"alert_rules": rules, "total": len(rules)}


@router.post("/alerts/rules", status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a new alert rule."""
    if not data.get("metric_id") or not data.get("name"):
        raise HTTPException(status_code=400, detail="Fields 'metric_id' and 'name' are required.")
    return analytics_service.create_alert_rule(tenant_id, data, db)


@router.get("/alerts/events")
def list_alert_events(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List triggered alert events."""
    events = analytics_service.list_alert_events(tenant_id, db)
    return {"alert_events": events, "total": len(events)}
