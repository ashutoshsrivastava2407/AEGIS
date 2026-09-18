"""Workflow Failure Classification and Exponential Backoff Retry Engine."""

import random
from typing import Dict, Any, Tuple


class WorkflowRetryEngine:
    """Classifies execution failures and calculates exponential backoff retry delays with jitter."""

    FAILURE_TYPES = {"TRANSIENT", "PERMANENT", "GOVERNANCE_REJECTED", "TIMEOUT"}

    def classify_failure(self, error: Dict[str, Any]) -> str:
        """Classify failure code or exception into actionable retry categories."""
        code = str(error.get("code", "")).upper()
        msg = str(error.get("message", "")).lower()

        if "timeout" in msg or "timeout" in code or code == "TIMED_OUT":
            return "TIMEOUT"
        elif "governance" in msg or "policy" in msg or code == "GOVERNANCE_REJECTED":
            return "GOVERNANCE_REJECTED"
        elif "permanent" in msg or "contract" in code or code == "ACTION_CONTRACT_VALIDATION_FAILED":
            return "PERMANENT"
        else:
            return "TRANSIENT"

    def should_retry(
        self,
        retry_count: int,
        error: Dict[str, Any],
        retry_policy: Dict[str, Any],
    ) -> Tuple[bool, float, str]:
        """Determine if a node should retry based on retry policy and failure classification.
        
        Returns:
            Tuple[should_retry, delay_seconds, failure_type]
        """
        failure_type = self.classify_failure(error)

        if failure_type in {"PERMANENT", "GOVERNANCE_REJECTED"}:
            return False, 0.0, failure_type

        max_retries = retry_policy.get("max_retries", 3)
        if retry_count >= max_retries:
            return False, 0.0, failure_type

        initial = retry_policy.get("initial_interval_seconds", 2)
        coeff = retry_policy.get("backoff_coefficient", 2.0)
        max_interval = retry_policy.get("max_interval_seconds", 60)

        raw_delay = initial * (coeff ** retry_count)
        capped_delay = min(raw_delay, max_interval)
        # Add 10% jitter
        jitter = random.uniform(0, 0.1 * capped_delay)
        final_delay = capped_delay + jitter

        return True, round(final_delay, 2), failure_type
