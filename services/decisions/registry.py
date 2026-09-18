"""Decision Lifecycle State Machine & Optimistic Concurrency Control Registry."""

from typing import Dict, Any, List, Optional
from packages.database.models.decision import DecisionModel


class DecisionRegistry:
    """Decision Registry managing lifecycle state machine transitions & concurrency."""

    VALID_TRANSITIONS = {
        "CREATED": ["CONTEXT_BUILDING", "BLOCKED", "CANCELLED"],
        "CONTEXT_BUILDING": ["EVALUATING", "BLOCKED", "CANCELLED"],
        "EVALUATING": ["SIMULATING", "PROPOSED", "BLOCKED", "CANCELLED"],
        "SIMULATING": ["PROPOSED", "BLOCKED", "CANCELLED"],
        "PROPOSED": ["PENDING_APPROVAL", "APPROVED", "REJECTED", "BLOCKED", "CANCELLED"],
        "PENDING_APPROVAL": ["APPROVED", "REJECTED", "EXPIRED", "BLOCKED", "CANCELLED"],
        "APPROVED": ["EXECUTING", "BLOCKED", "CANCELLED", "REOPENED"],
        "REJECTED": ["REOPENED", "CLOSED"],
        "EXECUTING": ["EXECUTED", "FAILED", "BLOCKED"],
        "EXECUTED": ["OBSERVING", "CLOSED"],
        "FAILED": ["REOPENED", "CLOSED"],
        "OBSERVING": ["CLOSED", "REOPENED"],
        "BLOCKED": ["CONTEXT_BUILDING", "EVALUATING", "REOPENED", "CANCELLED"],
        "EXPIRED": ["REOPENED", "CLOSED"],
        "CANCELLED": ["REOPENED"],
        "CLOSED": ["REOPENED"],
        "REOPENED": ["CONTEXT_BUILDING", "EVALUATING"],
    }

    def validate_transition(self, current_status: str, target_status: str) -> bool:
        """Validate whether state transition from current_status to target_status is allowed."""
        allowed = self.VALID_TRANSITIONS.get(current_status, [])
        return target_status in allowed

    def update_decision_state(
        self,
        decision: DecisionModel,
        target_status: str,
        expected_version: Optional[int] = None,
        rationale: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform optimistic-concurrency-checked state transition."""
        # 1. Optimistic concurrency check
        if expected_version is not None and decision.version != expected_version:
            return {
                "success": False,
                "error": f"Stale decision update error. Expected version {expected_version}, but current version is {decision.version}.",
                "stale": True
            }

        # 2. Validate lifecycle transition
        if not self.validate_transition(decision.decision_status, target_status):
            return {
                "success": False,
                "error": f"Invalid state transition from '{decision.decision_status}' to '{target_status}'.",
                "invalid_transition": True
            }

        # 3. Apply state transition and bump version
        old_status = decision.decision_status
        decision.decision_status = target_status
        decision.version += 1
        if rationale:
            decision.integrity_rationale = rationale

        return {
            "success": True,
            "previous_status": old_status,
            "new_status": target_status,
            "new_version": decision.version
        }
