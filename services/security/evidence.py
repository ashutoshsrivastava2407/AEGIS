"""Compliance Evidence Collector and Sealed Audit Package Engine."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from packages.database.models.compliance import EvidenceRecordModel, AuditPackageModel


class ComplianceEvidenceCollector:
    """Collects verifiable compliance evidence and packages sealed audit artifacts."""

    def collect_evidence(
        self,
        control_id: str,
        source_system: str,
        evidence_type: str,
        payload: Dict[str, Any],
        tenant_id: str = "default",
    ) -> EvidenceRecordModel:
        """Collect verifiable compliance evidence with SHA-256 checksum."""
        payload_str = json.dumps(payload, sort_keys=True)
        checksum = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        return EvidenceRecordModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            control_id=control_id,
            source_system=source_system,
            evidence_type=evidence_type.upper(),
            integrity_checksum=checksum,
            evidence_payload_json=payload,
            collected_at=datetime.now(timezone.utc).isoformat(),
            created_by="system",
            updated_by="system",
        )

    def seal_audit_package(
        self,
        package_name: str,
        framework_id: str,
        evidence_ids: List[str],
        tenant_id: str = "default",
    ) -> AuditPackageModel:
        """Seal evidence records into an immutable audit package."""
        canonical_raw = f"{framework_id}:{','.join(sorted(evidence_ids))}"
        sealed_checksum = hashlib.sha256(canonical_raw.encode("utf-8")).hexdigest()

        return AuditPackageModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            package_name=package_name,
            framework_id=framework_id,
            sealed_checksum=sealed_checksum,
            evidence_ids_json={"evidence_ids": evidence_ids},
            status="SEALED",
            sealed_at=datetime.now(timezone.utc).isoformat(),
            created_by="auditor",
            updated_by="auditor",
        )
