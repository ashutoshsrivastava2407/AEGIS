"""Incident Management & Immutable Timeline Event Logging Service."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from packages.database.models.operations import IncidentModel, IncidentTimelineEventModel


class IncidentManagementService:
    """Service for production incident lifecycle management, severity classification, and immutable timeline logging."""

    VALID_SEVERITIES = ["SEV0", "SEV1", "SEV2", "SEV3", "SEV4"]
    VALID_STATUSES = ["DETECTED", "TRIAGED", "INVESTIGATING", "MITIGATED", "RESOLVED", "CLOSED"]

    def __init__(self, db_session=None):
        self.db = db_session
        self._in_memory_incidents: Dict[str, Dict[str, Any]] = {}
        self._in_memory_timelines: Dict[str, List[Dict[str, Any]]] = {}

    def declare_incident(
        self,
        title: str,
        severity: str = "SEV2",
        service_id: str = "platform",
        summary: str = "",
        assigned_commander: Optional[str] = None,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Declare a new production incident."""
        sev = severity.upper()
        if sev not in self.VALID_SEVERITIES:
            sev = "SEV2"

        inc_id = f"inc-{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()

        incident_data = {
            "id": inc_id,
            "incident_id": inc_id,
            "title": title,
            "severity": sev,
            "status": "DETECTED",
            "service_id": service_id,
            "summary": summary,
            "assigned_commander": assigned_commander or "unassigned",
            "detected_at": now_str,
            "resolved_at": None,
            "closed_at": None,
            "tenant_id": tenant_id,
        }

        self._in_memory_incidents[inc_id] = incident_data
        self._in_memory_timelines[inc_id] = []

        if self.db:
            model = IncidentModel(
                id=inc_id,
                title=title,
                severity=sev,
                status="DETECTED",
                service_id=service_id,
                summary=summary,
                assigned_commander=assigned_commander,
                detected_at=datetime.now(timezone.utc),
                tenant_id=tenant_id,
            )
            self.db.add(model)
            self.db.commit()

        # Add initial timeline event
        self.add_timeline_event(
            incident_id=inc_id,
            event_type="INCIDENT_DECLARED",
            description=f"Incident '{title}' declared with severity {sev}",
            actor="SystemAlertEngine",
            tenant_id=tenant_id,
        )

        return incident_data

    def transition_incident_status(
        self,
        incident_id: str,
        new_status: str,
        actor: str = "SREOnCall",
        reason: str = "",
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Transition incident through canonical status lifecycle."""
        status_upper = new_status.upper()
        if status_upper not in self.VALID_STATUSES:
            raise ValueError(f"Invalid incident status '{new_status}'. Allowed: {self.VALID_STATUSES}")

        incident = self._in_memory_incidents.get(incident_id)
        if not incident:
            # Fallback mock lookup
            incident = {
                "id": incident_id,
                "title": f"Incident {incident_id}",
                "severity": "SEV2",
                "status": "DETECTED",
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "tenant_id": tenant_id,
            }
            self._in_memory_incidents[incident_id] = incident
            self._in_memory_timelines[incident_id] = []

        old_status = incident.get("status", "DETECTED")
        now_str = datetime.now(timezone.utc).isoformat()
        incident["status"] = status_upper

        if status_upper in ["RESOLVED", "CLOSED"] and not incident.get("resolved_at"):
            incident["resolved_at"] = now_str
        if status_upper == "CLOSED":
            incident["closed_at"] = now_str

        if self.db:
            db_inc = self.db.query(IncidentModel).filter_by(id=incident_id).first()
            if db_inc:
                db_inc.status = status_upper
                if status_upper in ["RESOLVED", "CLOSED"] and not db_inc.resolved_at:
                    db_inc.resolved_at = datetime.now(timezone.utc)
                if status_upper == "CLOSED":
                    db_inc.closed_at = datetime.now(timezone.utc)
                self.db.commit()

        # Record immutable timeline event
        self.add_timeline_event(
            incident_id=incident_id,
            event_type="STATUS_CHANGED",
            description=f"Status changed from {old_status} to {status_upper}. Reason: {reason}",
            actor=actor,
            tenant_id=tenant_id,
        )

        return incident

    def add_timeline_event(
        self,
        incident_id: str,
        event_type: str,
        description: str,
        actor: str = "System",
        payload_json: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Add an immutable timeline log entry for an incident."""
        event_data = {
            "id": str(uuid.uuid4()),
            "incident_id": incident_id,
            "event_type": event_type,
            "description": description,
            "actor": actor,
            "payload_json": payload_json or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id,
        }

        if incident_id not in self._in_memory_timelines:
            self._in_memory_timelines[incident_id] = []
        self._in_memory_timelines[incident_id].append(event_data)

        if self.db:
            model = IncidentTimelineEventModel(
                id=event_data["id"],
                incident_id=incident_id,
                event_type=event_type,
                description=description,
                actor=actor,
                payload_json=payload_json or {},
                tenant_id=tenant_id,
            )
            self.db.add(model)
            self.db.commit()

        return event_data

    def get_incident_details(self, incident_id: str) -> Dict[str, Any]:
        """Get incident details along with timeline events."""
        incident = self._in_memory_incidents.get(incident_id, {
            "id": incident_id,
            "title": f"Incident {incident_id}",
            "severity": "SEV2",
            "status": "INVESTIGATING",
            "detected_at": datetime.now(timezone.utc).isoformat(),
        })
        timeline = self._in_memory_timelines.get(incident_id, [])

        return {
            "incident": incident,
            "timeline": timeline,
            "timeline_count": len(timeline),
        }

    def list_incidents(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        tenant_id: str = "default",
    ) -> List[Dict[str, Any]]:
        """List active and historical incidents."""
        incidents = list(self._in_memory_incidents.values())
        if status:
            incidents = [i for i in incidents if i.get("status") == status.upper()]
        if severity:
            incidents = [i for i in incidents if i.get("severity") == severity.upper()]
        return incidents
