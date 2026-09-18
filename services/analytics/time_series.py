"""AEGIS Time-Series Analytics & Comparison Engine.

Provides windowed time-grain aggregations, moving averages, rolling growth rates, and period-over-period comparisons.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional


class TimeSeriesPoint:
    def __init__(self, timestamp: str, value: float, dimension_key: Optional[str] = None):
        self.timestamp = timestamp
        self.value = value
        self.dimension_key = dimension_key

    def to_dict(self) -> Dict[str, Any]:
        return {"timestamp": self.timestamp, "value": self.value, "dimension_key": self.dimension_key}


class TimeSeriesAnalyzer:
    """Time-series aggregation and comparative analytics."""

    @staticmethod
    def calculate_moving_average(points: List[float], window_size: int = 7) -> List[float]:
        """Compute rolling moving average over window."""
        if not points:
            return []
        res = []
        for i in range(len(points)):
            start_idx = max(0, i - window_size + 1)
            sub = points[start_idx : i + 1]
            res.append(round(sum(sub) / len(sub), 4))
        return res

    @staticmethod
    def calculate_growth_rate(current_val: float, previous_val: float) -> float:
        """Compute percentage growth rate between two values."""
        if previous_val == 0.0:
            return 0.0 if current_val == 0.0 else 100.0
        pct = ((current_val - previous_val) / abs(previous_val)) * 100.0
        return round(pct, 2)

    @staticmethod
    def compare_periods(
        current_series: List[float],
        previous_series: List[float]
    ) -> Dict[str, Any]:
        """Compute period-over-period comparison metrics."""
        curr_total = sum(current_series) if current_series else 0.0
        prev_total = sum(previous_series) if previous_series else 0.0
        
        curr_avg = (curr_total / len(current_series)) if current_series else 0.0
        prev_avg = (prev_total / len(previous_series)) if previous_series else 0.0

        pct_change = TimeSeriesAnalyzer.calculate_growth_rate(curr_total, prev_total)

        return {
            "current_total": round(curr_total, 2),
            "previous_total": round(prev_total, 2),
            "current_avg": round(curr_avg, 2),
            "previous_avg": round(prev_avg, 2),
            "percentage_change": pct_change,
            "direction": "INCREASING" if pct_change > 0 else ("DECREASING" if pct_change < 0 else "STABLE"),
        }
