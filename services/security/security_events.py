"""Structured Security Audit Event Logging Engine."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from packages.database.models.security import SecurityEventModel


class SecurityEventLogger:
    """Emits auditable security events (`AUTH_FAILURE`, `LOGIN`, `POLICY_CHANGED`, `SSRF_BLOCKED`, `BREAK_GLASS_USED`)."""

    EVENT_TYPES = {
        "AUTH_FAILURE", "LOGIN", "LOGOUT", "MFA_EVENT", "ROLE_CHANGED",
        "PERMISSION_CHANGED", "POLICY_CHANGED", "PRIVILEGE_ELEVATED",
        "DATA_EXPORT", "SENSITIVE_ACCESS", "SECRET_ACCESS", "CONNECTOR_BLOCKED",
        "SSRF_BLOCKED", "AGENT_PERMISSION_DENIED", "WORKFLOW_POLICY_DENIED",
        "ACTION_POLICY_DENIED", "BREAK_GLASS_USED"
    }

    def log_event(
        self,
        event_type: str,
        actor_id: str,
        severity: str = "INFO",
        resource_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
    ) -> SecurityEventModel:
        """Emit a structured, auditable security event."""
        etype = event_type.upper()
        cid = correlation_id or str(uuid.uuid4())

        return SecurityEventModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            event_type=etype,
            actor_id=actor_id,
            resource_id=resource_id,
            severity=severity.upper(),
            correlation_id=cid,
            details_json=details or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
            created_by=actor_id,
            updated_by=actor_id,
        )
