"""AEGIS Analytics & Intelligence Subsystem Package."""

from services.analytics.query_engine import ASTSQLGuard, AnalyticalQueryEngine, SQLSecurityValidationError
from services.analytics.datasets import AnalyticalDatasetRegistry
from services.analytics.metrics import MetricEngine
from services.analytics.time_series import TimeSeriesAnalyzer
from services.analytics.anomaly_detection import AnomalyDetector, ZScoreStrategy, EWMADetector, RollingThresholdStrategy
from services.analytics.trend_detection import TrendDetector
from services.analytics.insight_engine import InsightEngine
from services.analytics.alert_evaluator import AlertEvaluator
from services.analytics.realtime_integration import RealTimeAnalyticsAggregator
from services.analytics.services import AnalyticsDataPlatformService, analytics_service

__all__ = [
    "ASTSQLGuard",
    "AnalyticalQueryEngine",
    "SQLSecurityValidationError",
    "AnalyticalDatasetRegistry",
    "MetricEngine",
    "TimeSeriesAnalyzer",
    "AnomalyDetector",
    "ZScoreStrategy",
    "EWMADetector",
    "RollingThresholdStrategy",
    "TrendDetector",
    "InsightEngine",
    "AlertEvaluator",
    "RealTimeAnalyticsAggregator",
    "AnalyticsDataPlatformService",
    "analytics_service",
]
