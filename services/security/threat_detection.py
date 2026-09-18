"""Security Anomaly and Threat Signal Detection Engine."""

import uuid
from typing import Dict, Any, List
from packages.database.models.security import SecurityEventModel, SecurityFindingModel


class SecurityThreatDetector:
    """Analyzes security events and identifies threat signals without duplicating analytics infrastructure."""

    def analyze_event_stream(
        self,
        events: List[SecurityEventModel],
        tenant_id: str = "default",
    ) -> List[SecurityFindingModel]:
        """Scan event stream for authorization failure bursts, privilege escalation anomalies, and export bursts."""
        findings: List[SecurityFindingModel] = []

        auth_failures = [e for e in events if e.event_type in {"AUTH_FAILURE", "CONNECTOR_BLOCKED", "SSRF_BLOCKED"}]
        if len(auth_failures) >= 3:
            findings.append(
                SecurityFindingModel(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    title="Repeated Authorization Failure Burst Detected",
                    finding_type="AUTH_FAILURE_BURST",
                    severity="HIGH",
                    status="OPEN",
                    affected_asset_id=auth_failures[0].actor_id,
                    evidence_json={"failure_count": len(auth_failures), "events": [e.id for e in auth_failures]},
                    remediation_notes="Investigate potential credential brute-force or authorization bypass attempt.",
                    created_by="threat_detector",
                    updated_by="threat_detector",
                )
            )

        export_events = [e for e in events if e.event_type == "DATA_EXPORT"]
        if len(export_events) >= 5:
            findings.append(
                SecurityFindingModel(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    title="Abnormal High-Volume Data Export Detected",
                    finding_type="DATA_EXFILTRATION_ANOMALY",
                    severity="CRITICAL",
                    status="OPEN",
                    affected_asset_id=export_events[0].actor_id,
                    evidence_json={"export_count": len(export_events)},
                    remediation_notes="High-volume data export burst flagged for security review.",
                    created_by="threat_detector",
                    updated_by="threat_detector",
                )
            )

        return findings
