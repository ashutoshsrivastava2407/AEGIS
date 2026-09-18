"""Prometheus metrics exporter interface for AEGIS."""

from typing import Dict, Any


class MetricsExporter:
    """Telemetry metrics interface."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {}

    def increment(self, metric_name: str, value: int = 1) -> None:
        self._counters[metric_name] = self._counters.get(metric_name, 0) + value

    def get_metrics(self) -> Dict[str, Any]:
        return self._counters.copy()


metrics_exporter = MetricsExporter()
