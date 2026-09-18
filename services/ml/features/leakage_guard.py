"""AEGIS Training Data Leakage Protection Engine."""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class DataLeakageValidationError(Exception):
    """Raised when data leakage or temporal split rules are violated."""
    pass


class LeakageGuard:
    """Validates temporal correctness, target leakage, and training/serving split integrity."""

    @staticmethod
    def validate_target_leakage(feature_names: List[str], target_column: str) -> None:
        """Ensure target column is not included in feature definition set."""
        target_lower = target_column.lower().strip()
        for f in feature_names:
            if f.lower().strip() == target_lower:
                raise DataLeakageValidationError(
                    f"Target Leakage Detected: Target column '{target_column}' cannot be included in feature set."
                )

    @staticmethod
    def validate_temporal_split(
        train_timestamps: List[datetime],
        test_timestamps: List[datetime]
    ) -> bool:
        """Enforce point-in-time correctness: max(train_ts) <= min(test_ts)."""
        if not train_timestamps or not test_timestamps:
            return True

        max_train = max(train_timestamps)
        min_test = min(test_timestamps)

        if max_train > min_test:
            raise DataLeakageValidationError(
                f"Temporal Split Violation: Training timestamps (max {max_train.isoformat()}) "
                f"overlap with test timestamps (min {min_test.isoformat()}). Temporal splitting must be strictly sequential."
            )
        return True

    @staticmethod
    def validate_future_information(
        event_timestamp: datetime,
        cutoff_timestamp: datetime
    ) -> bool:
        """Prevent feature timestamp violations where event_timestamp > cutoff_timestamp."""
        if event_timestamp > cutoff_timestamp:
            raise DataLeakageValidationError(
                f"Future Information Leakage: Event timestamp {event_timestamp.isoformat()} "
                f"is after the point-in-time prediction cutoff {cutoff_timestamp.isoformat()}."
            )
        return True
