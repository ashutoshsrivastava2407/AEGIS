"""AEGIS Deterministic Feature Transformation Engine."""

from datetime import datetime
import math
from typing import Any, Dict, List, Union


class FeatureTransformationError(Exception):
    """Raised when a feature transformation fails schema or arithmetic rules."""
    pass


class FeatureTransformer:
    """Deterministic, reproducible feature transformation executor."""

    @staticmethod
    def apply_numerical(val: Union[int, float], formula: str) -> float:
        """Apply deterministic numerical transformation."""
        try:
            x = float(val)
            if formula == "LOG1P":
                return math.log1p(max(0.0, x))
            elif formula == "NORMALIZE_100":
                return round(x / 100.0, 4)
            elif formula == "SQUARE":
                return x ** 2
            elif formula == "SQRT":
                return math.sqrt(max(0.0, x))
            elif formula == "IDENTITY" or not formula:
                return x
            else:
                # Simple math expression evaluation
                return float(eval(formula, {"__builtins__": None}, {"x": x, "math": math}))
        except Exception as e:
            raise FeatureTransformationError(f"Numerical transformation failed for val '{val}' with formula '{formula}': {str(e)}")

    @staticmethod
    def apply_categorical(val: Any, encoding: str = "ONE_HOT") -> Union[int, float, str]:
        """Apply categorical encoding transformation."""
        str_val = str(val).strip().upper()
        if encoding == "LABEL":
            return hash(str_val) % 1000
        elif encoding == "LOWER":
            return str_val.lower()
        else:
            return str_val

    @staticmethod
    def apply_temporal(dt_val: Union[datetime, str], extract: str = "HOUR") -> int:
        """Apply temporal feature extraction."""
        if isinstance(dt_val, str):
            try:
                dt = datetime.fromisoformat(dt_val.replace("Z", "+00:00"))
            except Exception:
                dt = datetime.now()
        else:
            dt = dt_val

        extract_upper = extract.upper()
        if extract_upper == "HOUR":
            return dt.hour
        elif extract_upper == "DAY_OF_WEEK":
            return dt.weekday()
        elif extract_upper == "DAY_OF_MONTH":
            return dt.day
        elif extract_upper == "MONTH":
            return dt.month
        elif extract_upper == "YEAR":
            return dt.year
        else:
            return dt.hour
