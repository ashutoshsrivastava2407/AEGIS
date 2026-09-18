"""Time-Bounded, Governed Policy Exception Manager."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from packages.database.models.policy import SecurityPolicyExceptionModel


class PolicyExceptionManager:
    """Manages time-bounded, explicit policy exceptions with automatic expiration."""

    VALID_STATUSES = {"REQUESTED", "UNDER_REVIEW", "APPROVED", "ACTIVE", "EXPIRED", "REVOKED", "REJECTED"}

    def request_exception(
        self,
        policy_id: str,
        subject_id: str,
        resource_scope: str,
        justification: str,
        duration_days: int = 7,
        tenant_id: str = "default",
    ) -> SecurityPolicyExceptionModel:
        """Create a new policy exception request."""
        expires = (datetime.now(timezone.utc) + timedelta(days=duration_days)).isoformat()

        return SecurityPolicyExceptionModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            policy_id=policy_id,
            subject_id=subject_id,
            resource_scope=resource_scope,
            justification=justification,
            approved_by="pending",
            status="REQUESTED",
            expires_at=expires,
            created_by=subject_id,
            updated_by=subject_id,
        )

    def approve_exception(self, exception_model: SecurityPolicyExceptionModel, approved_by: str) -> SecurityPolicyExceptionModel:
        """Approve and activate policy exception."""
        exception_model.approved_by = approved_by
        exception_model.status = "ACTIVE"
        exception_model.updated_by = approved_by
        return exception_model

    def validate_exception_active(self, exception_model: SecurityPolicyExceptionModel) -> bool:
        """Verify policy exception is ACTIVE and not expired."""
        if exception_model.status != "ACTIVE":
            return False

        expires_dt = datetime.fromisoformat(exception_model.expires_at.replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires_dt:
            exception_model.status = "EXPIRED"
            return False

        return True
