"""Unit Tests for AEGIS Analytics & Intelligence Subsystem."""

import pytest
from services.analytics.query_engine import ASTSQLGuard, SQLSecurityValidationError
from services.analytics.anomaly_detection import ZScoreStrategy, EWMADetector, RollingThresholdStrategy
from services.analytics.metrics import MetricEngine
from services.analytics.trend_detection import TrendDetector
from services.analytics.time_series import TimeSeriesAnalyzer
from packages.database.models.metric_definition import MetricDefinitionModel


def test_ast_sql_guard_valid_select():
    """Verify ASTSQLGuard permits valid SELECT queries and injects tenant filter."""
    sql = "SELECT region, SUM(amount) AS total FROM gold_analytics_sales GROUP BY region"
    
    ast_meta = ASTSQLGuard.validate_ast(sql, allowed_tables={"gold_analytics_sales", "silver_orders"})
    assert ast_meta["valid"] is True
    assert "gold_analytics_sales" in ast_meta["referenced_tables"]

    secured_sql = ASTSQLGuard.inject_tenant_predicate_and_limit(sql, tenant_id="tenant_alpha", max_rows=1000)
    assert "WHERE tenant_id = 'tenant_alpha'" in secured_sql
    assert "LIMIT 1000" in secured_sql


def test_ast_sql_guard_blocks_ddl_dml():
    """Verify ASTSQLGuard rejects destructive DDL/DML operations."""
    allowed = {"gold_analytics_sales"}
    
    destructive_queries = [
        "DROP TABLE gold_analytics_sales",
        "DELETE FROM gold_analytics_sales WHERE id = 1",
        "UPDATE gold_analytics_sales SET amount = 0",
        "INSERT INTO gold_analytics_sales VALUES (1, 'test', 100)",
        "ALTER TABLE gold_analytics_sales ADD COLUMN secret TEXT",
        "TRUNCATE TABLE gold_analytics_sales",
    ]
    
    for query in destructive_queries:
        with pytest.raises(SQLSecurityValidationError):
            ASTSQLGuard.validate_ast(query, allowed_tables=allowed)


def test_ast_sql_guard_disallowed_table():
    """Verify ASTSQLGuard blocks queries targeting unapproved tables."""
    allowed = {"gold_analytics_sales"}
    unauthorized_query = "SELECT * FROM secret_user_credentials"
    
    with pytest.raises(SQLSecurityValidationError) as exc:
        ASTSQLGuard.validate_ast(unauthorized_query, allowed_tables=allowed)
    assert "unauthorized" in str(exc.value).lower() or "secret_user_credentials" in str(exc.value).lower()


def test_ast_sql_guard_multi_statement_rejection():
    """Verify ASTSQLGuard rejects multi-statement SQL injection attempts."""
    allowed = {"gold_analytics_sales"}
    multi_stmt = "SELECT * FROM gold_analytics_sales; DROP TABLE gold_analytics_sales;"
    
    with pytest.raises(SQLSecurityValidationError):
        ASTSQLGuard.validate_ast(multi_stmt, allowed_tables=allowed)


def test_zscore_strategy_math():
    """Verify ZScoreStrategy formula z = (x - mu) / sigma and anomaly scoring."""
    strategy = ZScoreStrategy(z_threshold=2.0)
    history = [10.0, 11.0, 9.0, 10.5, 9.5]
    outlier = 100.0  # Clear outlier
    
    res = strategy.detect(outlier, history)
    assert res.is_anomaly is True
    assert res.observed_value == 100.0
    assert res.z_score > 2.0


def test_zscore_strategy_zero_variance():
    """Verify ZScoreStrategy safely handles zero-variance datasets without division by zero."""
    strategy = ZScoreStrategy(z_threshold=2.0)
    history = [5.0, 5.0, 5.0, 5.0]
    current = 5.0
    
    res = strategy.detect(current, history)
    assert res.is_anomaly is False
    assert res.z_score == 0.0


def test_ewma_detector():
    """Verify EWMADetector identifies sudden shifts from exponentially weighted average."""
    detector = EWMADetector(alpha=0.3, threshold_mult=2.0)
    history = [50.0, 51.0, 49.0, 50.0, 52.0]
    outlier = 150.0
    
    res = detector.detect(outlier, history)
    assert res.is_anomaly is True
    assert res.detection_method == "EWMA"


def test_rolling_threshold_strategy():
    """Verify RollingThresholdStrategy flags values exceeding window bounds."""
    strategy = RollingThresholdStrategy(min_bound=0.0, max_bound=100.0)
    history = [10.0, 20.0, 30.0]
    
    res_normal = strategy.detect(50.0, history)
    assert res_normal.is_anomaly is False

    res_breach = strategy.detect(150.0, history)
    assert res_breach.is_anomaly is True


def test_metric_engine_aggregations():
    """Verify MetricEngine standard aggregations SUM, AVG, COUNT, MIN, MAX."""
    values = [10.0, 20.0, 30.0, 40.0, 50.0]

    def make_metric(agg_type):
        return MetricDefinitionModel(
            tenant_id="t1", name="m", aggregation_type=agg_type,
            time_grain="DAY", calculation_formula=f"{agg_type}(v)"
        )

    assert MetricEngine.calculate(make_metric("SUM"), values) == 150.0
    assert MetricEngine.calculate(make_metric("AVG"), values) == 30.0
    assert MetricEngine.calculate(make_metric("COUNT"), values) == 5.0
    assert MetricEngine.calculate(make_metric("MIN"), values) == 10.0
    assert MetricEngine.calculate(make_metric("MAX"), values) == 50.0


def test_trend_detector():
    """Verify TrendDetector computes linear slope, acceleration, and trend direction."""
    # Increasing trend
    increasing_series = [10.0, 20.0, 30.0, 40.0, 50.0]
    res_inc = TrendDetector.analyze_trend(increasing_series)
    assert res_inc.direction in ["INCREASING", "ACCELERATING"]
    assert res_inc.slope > 0
    
    # Decreasing trend
    decreasing_series = [100.0, 80.0, 60.0, 40.0, 20.0]
    res_dec = TrendDetector.analyze_trend(decreasing_series)
    assert res_dec.direction in ["DECREASING", "DECELERATING"]
    assert res_dec.slope < 0


def test_time_series_analyzer():
    """Verify TimeSeriesAnalyzer moving averages and growth rates."""
    series = [10.0, 20.0, 30.0, 40.0, 50.0]
    
    ma = TimeSeriesAnalyzer.calculate_moving_average(series, window_size=3)
    assert len(ma) == len(series)
    assert ma[2] == pytest.approx(20.0)  # (10 + 20 + 30)/3
    
    growth = TimeSeriesAnalyzer.calculate_growth_rate(150.0, 100.0)
    assert growth == pytest.approx(50.0)  # 50% growth
