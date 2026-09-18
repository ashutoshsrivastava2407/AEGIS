"""AEGIS Algorithmic Trend Detector Engine.

Computes linear regression slope and second-order acceleration across metric time-series.
"""

import math
from typing import Dict, Any, List


class TrendResult:
    def __init__(self, direction: str, slope: float, acceleration: float, confidence: float):
        self.direction = direction
        self.slope = slope
        self.acceleration = acceleration
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "direction": self.direction,
            "slope": round(self.slope, 4),
            "acceleration": round(self.acceleration, 4),
            "confidence": round(self.confidence, 2),
        }


class TrendDetector:
    """Algorithmic trend direction and acceleration calculator."""

    @staticmethod
    def analyze_trend(series: List[float]) -> TrendResult:
        """Compute slope and acceleration over series."""
        n = len(series)
        if n < 2:
            return TrendResult("STABLE", 0.0, 0.0, 1.0)

        x_vals = list(range(n))
        y_vals = series

        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
        sum_x2 = sum(x ** 2 for x in x_vals)

        denom = (n * sum_x2) - (sum_x ** 2)
        if denom == 0:
            slope = 0.0
        else:
            slope = ((n * sum_xy) - (sum_x * sum_y)) / float(denom)

        # Acceleration (slope difference between first half and second half)
        mid = n // 2
        first_half = series[:mid]
        second_half = series[mid:]

        slope_first = TrendDetector.analyze_trend(first_half).slope if len(first_half) >= 2 else slope
        slope_second = TrendDetector.analyze_trend(second_half).slope if len(second_half) >= 2 else slope
        acceleration = slope_second - slope_first

        # Classify direction
        avg_y = abs(sum_y / float(n)) if sum_y != 0 else 1.0
        rel_slope = (slope / avg_y) if avg_y != 0 else slope

        if rel_slope > 0.05:
            direction = "ACCELERATING" if acceleration > 0.01 else "INCREASING"
        elif rel_slope < -0.05:
            direction = "DECELERATING" if acceleration < -0.01 else "DECREASING"
        else:
            direction = "STABLE"

        return TrendResult(
            direction=direction,
            slope=slope,
            acceleration=acceleration,
            confidence=min(1.0, 0.5 + (n * 0.05)),
        )
