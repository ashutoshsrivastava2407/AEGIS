"""Workflow Trigger Engine and Deduplicated Event Inbox Service."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Tuple
from packages.database.models.workflow_trigger import WorkflowTriggerModel, WorkflowEventInboxModel


class WorkflowTriggerEngine:
    """Manages workflow trigger registration and transactional event inbox deduplication."""

    def register_trigger(
        self,
        workflow_id: str,
        trigger_type: str,
        event_topic: Optional[str] = None,
        deduplication_key: Optional[str] = None,
        trigger_config_json: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
    ) -> WorkflowTriggerModel:
        """Register a trigger mapping for a workflow."""
        return WorkflowTriggerModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            trigger_type=trigger_type.upper(),
            event_topic=event_topic,
            deduplication_key=deduplication_key,
            trigger_config_json=trigger_config_json or {},
            is_enabled=True,
            created_by="system",
            updated_by="system",
        )

    def process_incoming_event(
        self,
        event_id: str,
        deduplication_key: str,
        source: str,
        payload: Dict[str, Any],
        processed_inbox_keys: Set[str],
        tenant_id: str = "default",
    ) -> Tuple[bool, Optional[WorkflowEventInboxModel], str]:
        """Process incoming event through deduplication inbox.
        
        Returns:
            Tuple[is_duplicate, inbox_model, payload_hash]
        """
        payload_str = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        dedup_id = f"{tenant_id}:{event_id}:{deduplication_key}"

        if dedup_id in processed_inbox_keys or event_id in processed_inbox_keys:
            return True, None, payload_hash

        processed_inbox_keys.add(dedup_id)
        processed_inbox_keys.add(event_id)

        inbox_model = WorkflowEventInboxModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            event_id=event_id,
            deduplication_key=deduplication_key,
            source=source,
            payload_hash=payload_hash,
            processed_at=datetime.now(timezone.utc).isoformat(),
            status="PROCESSED",
            created_by=source,
            updated_by=source,
        )

        return False, inbox_model, payload_hash
