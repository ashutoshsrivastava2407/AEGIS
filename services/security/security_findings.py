"""Security Finding Lifecycle Management Engine."""

import uuid
from typing import Dict, Any, List, Optional
from packages.database.models.security import SecurityFindingModel


class SecurityFindingManager:
    """Manages security findings, severity triage, and remediation state transitions."""

    VALID_STATUSES = {"OPEN", "TRIAGED", "INVESTIGATING", "CONTAINED", "REMEDIATED", "ACCEPTED_RISK", "CLOSED"}

    def create_finding(
        self,
        title: str,
        finding_type: str,
        affected_asset_id: str,
        severity: str = "HIGH",
        evidence: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
    ) -> SecurityFindingModel:
        """Create a new security finding."""
        return SecurityFindingModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            title=title,
            finding_type=finding_type,
            severity=severity.upper(),
            status="OPEN",
            affected_asset_id=affected_asset_id,
            evidence_json=evidence or {},
            remediation_notes=None,
            created_by="security_threat_detector",
            updated_by="security_threat_detector",
        )

    def transition_finding_status(
        self,
        finding: SecurityFindingModel,
        target_status: str,
        notes: Optional[str] = None,
        updated_by: str = "security-analyst",
    ) -> SecurityFindingModel:
        """Transition finding state."""
        st = target_status.upper()
        if st not in self.VALID_STATUSES:
            raise ValueError(f"Invalid finding status: {st}")

        finding.status = st
        if notes:
            finding.remediation_notes = notes
        finding.updated_by = updated_by
        return finding
