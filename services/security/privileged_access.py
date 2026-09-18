"""Temporary Privileged Access Elevation and Emergency Break-Glass Controls."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from packages.database.models.governance import PrivilegedAccessRequestModel
from packages.database.models.security import BreakGlassSessionModel, BreakGlassReviewModel


class PrivilegedAccessManager:
    """Manages temporary privilege elevation requests."""

    def request_elevation(
        self,
        requester_id: str,
        role_requested: str,
        justification: str,
        duration_hours: int = 4,
        tenant_id: str = "default",
    ) -> PrivilegedAccessRequestModel:
        """Create a temporary privilege elevation request."""
        return PrivilegedAccessRequestModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            requester_id=requester_id,
            role_requested=role_requested,
            justification=justification,
            duration_hours=duration_hours,
            status="PENDING",
            approved_by=None,
            expires_at=None,
            created_by=requester_id,
            updated_by=requester_id,
        )

    def approve_elevation(self, request: PrivilegedAccessRequestModel, approver_id: str) -> PrivilegedAccessRequestModel:
        """Approve and activate elevation request."""
        request.approved_by = approver_id
        request.status = "ACTIVE"
        request.expires_at = (datetime.now(timezone.utc) + timedelta(hours=request.duration_hours)).isoformat()
        request.updated_by = approver_id
        return request


class BreakGlassManager:
    """Manages emergency break-glass elevated sessions with audit log tracking and post-use review lifecycle."""

    def __init__(self):
        self._reviews: Dict[str, Dict[str, Any]] = {}

    def activate_break_glass(
        self,
        actor_id: str,
        justification: str,
        scope_restricted: str = "PRODUCTION_HOTFIX",
        duration_minutes: int = 60,
        tenant_id: str = "default",
    ) -> BreakGlassSessionModel:
        """Activate elevated break-glass emergency session and automatically initialize post-use review item."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=duration_minutes)
        session_id = str(uuid.uuid4())

        session = BreakGlassSessionModel(
            id=session_id,
            tenant_id=tenant_id,
            actor_id=actor_id,
            justification=justification,
            scope_restricted=scope_restricted,
            status="ACTIVE",
            activated_at=now.isoformat(),
            expires_at=expires.isoformat(),
            created_by=actor_id,
            updated_by=actor_id,
        )

        # Initialize post-use review record
        review_id = str(uuid.uuid4())
        self._reviews[session_id] = {
            "review_id": review_id,
            "session_id": session_id,
            "tenant_id": tenant_id,
            "user_id": actor_id,
            "justification": justification,
            "resources_touched_json": [scope_restricted],
            "actions_executed_json": ["EMERGENCY_ACCESS_ACTIVATED"],
            "policies_overridden_json": ["APPROVAL_POLICY_OVERRIDDEN"],
            "activated_at": now.isoformat(),
            "expired_at": expires.isoformat(),
            "reviewer_id": None,
            "review_status": "PENDING_REVIEW",
            "review_notes": None,
            "closed_at": None,
        }

        return session

    def validate_session(self, session: BreakGlassSessionModel) -> bool:
        """Verify break-glass session is active and not expired."""
        if session.status != "ACTIVE":
            return False

        exp = datetime.fromisoformat(session.expires_at.replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > exp:
            session.status = "EXPIRED"
            return False

        return True

    def submit_post_use_review(
        self,
        session_id: str,
        reviewer_id: str,
        status: str = "CLOSED",  # PENDING_REVIEW, UNDER_REVIEW, ACCEPTED, REQUIRES_REMEDIATION, CLOSED
        review_notes: str = "Emergency break-glass session reviewed and justified.",
    ) -> Dict[str, Any]:
        """Submit auditor review for expired/closed break-glass session."""
        review = self._reviews.get(session_id)
        if not review:
            raise ValueError(f"Review record for break-glass session {session_id} not found.")

        review["reviewer_id"] = reviewer_id
        review["review_status"] = status.upper()
        review["review_notes"] = review_notes
        review["closed_at"] = datetime.now(timezone.utc).isoformat()
        return review

    def get_review_record(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve post-use review record for break-glass session."""
        return self._reviews.get(session_id)
