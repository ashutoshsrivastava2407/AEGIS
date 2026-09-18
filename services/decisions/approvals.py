"""Multi-Party Approval Gate Engine & TOCTOU Pre-Execution Revalidation."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone


class DecisionApprovalEngine:
    """Manages Decision Approvals and TOCTOU pre-execution revalidation."""

    @staticmethod
    def process_approval_action(
        decision_id: str,
        approver_id: str,
        approver_role: str,
        action: str,  # APPROVE, REJECT
        rationale: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process approval or rejection signoff."""
        if action == "REJECT":
            return {
                "approval_status": "REJECTED",
                "approver_id": approver_id,
                "approved_at": None,
                "rationale": rationale or "Decision rejected by approver."
            }
        elif action == "APPROVE":
            now_iso = datetime.now(timezone.utc).isoformat()
            return {
                "approval_status": "APPROVED",
                "approver_id": approver_id,
                "approved_at": now_iso,
                "rationale": rationale or f"Approved by {approver_id} ({approver_role})."
            }
        else:
            return {
                "approval_status": "PENDING",
                "approver_id": None,
                "approved_at": None,
                "rationale": f"Unknown approval action '{action}'."
            }

    @staticmethod
    def revalidate_approval_before_execution(
        approval_record: Dict[str, Any],
        context_fingerprint_at_approval: str,
        current_context_fingerprint: str,
        is_model_drifted: bool = False,
        is_policy_changed: bool = False
    ) -> Dict[str, Any]:
        """Perform TOCTOU revalidation immediately before execution."""
        if approval_record.get("approval_status") != "APPROVED":
            return {
                "is_valid": False,
                "status": "APPROVAL_INVALIDATED",
                "reason": "Decision was not in APPROVED status."
            }

        revalidation_failures = []

        # 1. Context fingerprint match check
        if context_fingerprint_at_approval != current_context_fingerprint:
            revalidation_failures.append("Context fingerprint mismatch (decision inputs modified after approval)")

        # 2. Model drift check
        if is_model_drifted:
            revalidation_failures.append("Model drift detected after approval signoff")

        # 3. Policy version check
        if is_policy_changed:
            revalidation_failures.append("Governance policy updated after approval signoff")

        if revalidation_failures:
            return {
                "is_valid": False,
                "status": "APPROVAL_INVALIDATED",
                "reason": "; ".join(revalidation_failures),
                "revalidation_failures": revalidation_failures
            }

        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            "is_valid": True,
            "status": "APPROVED",
            "revalidated_at": now_iso,
            "reason": "Pre-execution TOCTOU revalidation passed successfully."
        }
