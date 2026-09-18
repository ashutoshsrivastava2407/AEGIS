"""Periodic Access Certification Review Campaign Manager."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from packages.database.models.authorization import AccessReviewModel


class AccessReviewManager:
    """Manages periodic access certification campaigns for users, roles, and service identities."""

    def open_campaign(
        self,
        review_name: str,
        reviewer_id: str,
        target_subject_id: str,
        due_days: int = 14,
        tenant_id: str = "default",
    ) -> AccessReviewModel:
        """Create a new access certification review campaign."""
        due_at = (datetime.now(timezone.utc) + timedelta(days=due_days)).isoformat()

        return AccessReviewModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            review_name=review_name,
            reviewer_id=reviewer_id,
            target_subject_id=target_subject_id,
            status="REVIEW_OPENED",
            findings_json={"excessive_permissions": [], "unused_roles": []},
            due_at=due_at,
            created_by=reviewer_id,
            updated_by=reviewer_id,
        )

    def complete_review(
        self,
        review: AccessReviewModel,
        status: str,
        findings: Dict[str, Any],
        completed_by: str,
    ) -> AccessReviewModel:
        """Complete access review campaign."""
        st = status.upper()
        if st not in {"APPROVED", "REMEDIATION", "CLOSED"}:
            raise ValueError(f"Invalid access review completion status: {st}")

        review.status = st
        review.findings_json = findings
        review.updated_by = completed_by
        return review
