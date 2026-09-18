"""Security Audit Event Recorder."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from packages.observability import logger


class SecurityAuditRecorder:
    def record_event(
        self,
        event_type: str,
        actor_id: str,
        tenant_id: str,
        resource_id: str,
        action: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        audit_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "actor_id": actor_id,
            "tenant_id": tenant_id,
            "resource_id": resource_id,
            "action": action,
            "status": status,
            "details": details or {},
        }
        logger.info(f"AUDIT_EVENT: {event_type} - {action} - {status}", extra={"extra_fields": audit_event})
        return audit_event


audit_recorder = SecurityAuditRecorder()
