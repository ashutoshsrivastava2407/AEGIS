"""AEGIS Human-in-the-Loop Risk Classifier & Approval Gate Engine.

Enforces mandatory human authorization gates for high-risk actions.
Manages approval lifecycle: PENDING -> APPROVED / REJECTED / EXPIRED.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import uuid
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("aegis.agents.approvals.engine")


@dataclass
class ApprovalRequest:
    approval_id: str
    run_id: str
    plan_id: Optional[str]
    node_key: Optional[str]
    tool_name: str
    risk_level: str
    requested_action: str
    justification: str
    approval_status: str  # PENDING, APPROVED, REJECTED, EXPIRED
    created_at: str
    expires_at: Optional[str] = None
    approved_by: Optional[str] = None
    comments: Optional[str] = None


class HumanApprovalEngine:
    """Manages risk evaluation and human approval gates for agent executions."""

    def __init__(self):
        self._pending_approvals: Dict[str, ApprovalRequest] = {}

    def create_approval_request(
        self,
        run_id: str,
        tool_name: str,
        risk_level: str,
        requested_action: str,
        justification: str = "Agent requested high-risk action execution",
        plan_id: Optional[str] = None,
        node_key: Optional[str] = None,
        ttl_minutes: int = 60
    ) -> ApprovalRequest:
        """Create a pending human approval request."""
        approval_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=ttl_minutes)

        req = ApprovalRequest(
            approval_id=approval_id,
            run_id=run_id,
            plan_id=plan_id,
            node_key=node_key,
            tool_name=tool_name,
            risk_level=risk_level,
            requested_action=requested_action,
            justification=justification,
            approval_status="PENDING",
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat()
        )

        self._pending_approvals[approval_id] = req
        logger.info(f"Created pending approval request '{approval_id}' for tool '{tool_name}' (risk: {risk_level})")
        return req

    def approve_request(self, approval_id: str, approved_by: str = "admin", comments: str = "Approved by human operator") -> ApprovalRequest:
        """Approve a pending request."""
        req = self._pending_approvals.get(approval_id)
        if not req:
            raise ValueError(f"Approval request '{approval_id}' not found.")
        
        req.approval_status = "APPROVED"
        req.approved_by = approved_by
        req.comments = comments
        logger.info(f"Approval request '{approval_id}' APPROVED by '{approved_by}'")
        return req

    def reject_request(self, approval_id: str, rejected_by: str = "admin", comments: str = "Rejected by policy or human operator") -> ApprovalRequest:
        """Reject a pending request."""
        req = self._pending_approvals.get(approval_id)
        if not req:
            raise ValueError(f"Approval request '{approval_id}' not found.")
        
        req.approval_status = "REJECTED"
        req.approved_by = rejected_by
        req.comments = comments
        logger.info(f"Approval request '{approval_id}' REJECTED by '{rejected_by}'")
        return req

    def get_approval(self, approval_id: str) -> Optional[ApprovalRequest]:
        return self._pending_approvals.get(approval_id)

    def list_pending_approvals(self, run_id: Optional[str] = None) -> List[ApprovalRequest]:
        result = [req for req in self._pending_approvals.values() if req.approval_status == "PENDING"]
        if run_id:
            result = [req for req in result if req.run_id == run_id]
        return result


approval_engine = HumanApprovalEngine()
