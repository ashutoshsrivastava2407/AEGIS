"""Integration Tests for AEGIS Analytics & Intelligence End-to-End Pipeline."""

import pytest
from sqlalchemy import text
from packages.database.session import SessionLocal
from services.analytics.services import analytics_service


def test_end_to_end_analytics_pipeline():
    tenant_id = "tenant_analytics_qa_01"
    db = SessionLocal()

    try:
        # 1. Get initial overview
        overview = analytics_service.get_overview(tenant_id, db)
        assert overview is not None
        assert overview["status"] == "OPERATIONAL"

        # 2. Register Analytical Dataset
        dataset_data = {
            "name": "Gold Enterprise Financials",
            "target_table": "gold_analytics_sales",
            "description": "Daily enterprise revenue, costs, and profit metrics",
            "schema_json": {
                "transaction_date": "DATE",
                "revenue": "FLOAT",
                "cost": "FLOAT",
                "region": "VARCHAR(50)",
            },
        }
        dataset = analytics_service.create_dataset(tenant_id, dataset_data, db)
        assert dataset["id"] is not None
        assert dataset["name"] == "Gold Enterprise Financials"

        # 3. Register Metric Definition
        metric_data = {
            "name": "Daily Total Revenue",
            "dataset_id": dataset["id"],
            "aggregation_type": "SUM",
            "calculation_formula": "SUM(revenue)",
            "unit": "USD",
            "time_grain": "DAY",
            "dimensions": ["region"],
        }
        metric = analytics_service.create_metric(tenant_id, metric_data, db)
        assert metric["id"] is not None
        assert metric["name"] == "Daily Total Revenue"

        # 4. Evaluate Metric (Calculate value, check trend, run anomaly detection, generate insight)
        eval_res = analytics_service.evaluate_metric(
            tenant_id=tenant_id,
            metric_id=metric["id"],
            db=db,
            history_series=[100.0, 102.0, 101.5, 105.0, 108.0, 107.0, 250.0],  # 250.0 is an anomaly
        )
        assert eval_res["metric_id"] == metric["id"]
        assert eval_res["value"] == 873.5  # SUM of history series
        assert eval_res["anomaly_detected"] is True
        assert eval_res["insight_id"] is not None

        # 5. Execute AST SQL Guard Validated Query
        db.execute(text("CREATE TABLE IF NOT EXISTS gold_analytics_sales (id TEXT, tenant_id TEXT, region TEXT, revenue REAL)"))
        db.commit()

        sql = "SELECT region, SUM(revenue) as total_rev FROM gold_analytics_sales GROUP BY region"
        query_res = analytics_service.execute_analytical_query(
            tenant_id=tenant_id,
            sql_text=sql,
            parameters={},
            user_id="qa_analyst",
            db=db,
        )
        assert "rows" in query_res
        assert query_res["row_count"] >= 0
        assert "secured_sql" in query_res

        # 6. List Anomalies & Insights
        anomalies = analytics_service.list_anomalies(tenant_id, db)
        assert len(anomalies) >= 1

        insights = analytics_service.list_insights(tenant_id, db)
        assert len(insights) >= 1

        # 7. Dashboards
        dashboard_data = {"title": "Executive Overview Board", "description": "High level KPIs"}
        db_created = analytics_service.create_dashboard(tenant_id, dashboard_data, db)
        assert db_created["id"] is not None

        dashboards = analytics_service.list_dashboards(tenant_id, db)
        assert len(dashboards) >= 1

    finally:
        db.close()
