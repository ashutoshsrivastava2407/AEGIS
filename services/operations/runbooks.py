"""Operational Runbook Registry Service."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from packages.database.models.operations import RunbookModel


class RunbookRegistryService:
    """Service for registering, matching, and managing operational runbooks."""

    def __init__(self, db_session=None):
        self.db = db_session
        self._in_memory_runbooks: Dict[str, Dict[str, Any]] = {}
        self._execution_history: List[Dict[str, Any]] = []

    def register_runbook(
        self,
        title: str,
        service_id: str,
        trigger_condition: str,
        steps: List[Dict[str, Any]],
        automated_remediation_action: Optional[str] = None,
        author: str = "SRETeam",
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Register a new operational runbook."""
        runbook_id = f"rbk-{uuid.uuid4().hex[:12]}"
        runbook_data = {
            "id": runbook_id,
            "runbook_id": runbook_id,
            "title": title,
            "service_id": service_id,
            "trigger_condition": trigger_condition,
            "steps": steps,
            "automated_remediation_action": automated_remediation_action,
            "author": author,
            "version": "1.0.0",
            "tenant_id": tenant_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._in_memory_runbooks[runbook_id] = runbook_data

        if self.db:
            model = RunbookModel(
                id=runbook_id,
                title=title,
                service_id=service_id,
                trigger_condition=trigger_condition,
                steps_json=steps,
                automated_remediation_action=automated_remediation_action,
                author=author,
                version="1.0.0",
                tenant_id=tenant_id,
            )
            self.db.add(model)
            self.db.commit()

        return runbook_data

    def match_runbook(
        self,
        service_id: str,
        trigger_condition: str,
        tenant_id: str = "default",
    ) -> Optional[Dict[str, Any]]:
        """Find matching runbook for a service trigger condition."""
        for rbk in self._in_memory_runbooks.values():
            if rbk.get("tenant_id", "default") == tenant_id and rbk.get("service_id") == service_id:
                if trigger_condition.lower() in rbk.get("trigger_condition", "").lower():
                    return rbk
        return None

    def list_runbooks(
        self,
        service_id: Optional[str] = None,
        tenant_id: str = "default",
    ) -> List[Dict[str, Any]]:
        """List registered runbooks."""
        runbooks = list(self._in_memory_runbooks.values())
        if service_id:
            runbooks = [r for r in runbooks if r.get("service_id") == service_id]
        return runbooks

    def record_runbook_execution(
        self,
        runbook_id: str,
        incident_id: Optional[str],
        executed_by: str,
        status: str = "SUCCESS",
        results: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Record runbook execution record."""
        record = {
            "id": str(uuid.uuid4()),
            "runbook_id": runbook_id,
            "incident_id": incident_id,
            "executed_by": executed_by,
            "status": status,
            "results": results or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id,
        }
        self._execution_history.append(record)
        return record
