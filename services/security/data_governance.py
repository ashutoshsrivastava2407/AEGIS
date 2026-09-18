"""Data Governance, Classification, Masking, Residency, Legal Hold, and PII Protection Engine."""

import re
import uuid
from typing import Dict, Any, List, Optional
from packages.database.models.governance import DataClassificationModel, RetentionPolicyModel, LegalHoldModel


class DataGovernanceEngine:
    """Enforces classification-driven access controls, sensitive field masking, residency gating, and legal hold rules."""

    CLASSIFICATION_LEVELS = {"PUBLIC": 1, "INTERNAL": 2, "CONFIDENTIAL": 3, "RESTRICTED": 4}
    PII_PATTERNS = [
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),  # Email
        re.compile(r"\b(?:\d[ -]*?){13,16}\b"),  # Credit Card
    ]

    def __init__(self):
        self._legal_holds: Dict[str, Dict[str, Any]] = {}

    def create_classification(
        self,
        resource_type: str,
        resource_id: str,
        classification_level: str = "INTERNAL",
        contains_pii: bool = False,
        residency_region: str = "US",
        tenant_id: str = "default",
    ) -> DataClassificationModel:
        """Register or update resource data classification."""
        level = classification_level.upper()
        if level not in self.CLASSIFICATION_LEVELS:
            raise ValueError(f"Invalid classification level: {level}")

        return DataClassificationModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            resource_type=resource_type.upper(),
            resource_id=resource_id,
            classification_level=level,
            contains_pii=contains_pii,
            residency_region=residency_region.upper(),
            policy_tags_json={"tags": [level, residency_region.upper()]},
            created_by="system",
            updated_by="system",
        )

    def mask_sensitive_payload(self, data: Dict[str, Any], user_role: str = "USER") -> Dict[str, Any]:
        """Apply recursive column/field/nested-object/array-level masking based on user role and data sensitivity."""
        if user_role == "ENTERPRISE_ADMIN":
            return data

        masked = {}
        for k, v in data.items():
            key_lower = k.lower()
            if any(s in key_lower for s in ["ssn", "credit_card", "password", "secret", "token", "salary"]):
                masked[k] = "***MASKED***"
            elif isinstance(v, str):
                s_val = v
                for pat in self.PII_PATTERNS:
                    s_val = pat.sub("[REDACTED_PII]", s_val)
                masked[k] = s_val
            elif isinstance(v, dict):
                masked[k] = self.mask_sensitive_payload(v, user_role)
            elif isinstance(v, list):
                masked[k] = [
                    self.mask_sensitive_payload(item, user_role) if isinstance(item, dict)
                    else (self._mask_string_val(item) if isinstance(item, str) else item)
                    for item in v
                ]
            else:
                masked[k] = v
        return masked

    def _mask_string_val(self, val: str) -> str:
        s_val = val
        for pat in self.PII_PATTERNS:
            s_val = pat.sub("[REDACTED_PII]", s_val)
        return s_val

    def validate_export_permission(self, classification_level: str, user_role: str) -> bool:
        """Verify export authorization for sensitive datasets."""
        level = classification_level.upper()
        if level == "RESTRICTED" and user_role != "ENTERPRISE_ADMIN":
            return False
        return True

    def validate_data_residency(
        self,
        resource_residency: str,
        execution_region: str,
        allow_cross_border: bool = False,
    ) -> Dict[str, Any]:
        """Validate data residency compliance for resource processing."""
        res_upper = resource_residency.upper()
        exec_upper = execution_region.upper()

        if res_upper == exec_upper or allow_cross_border or res_upper == "GLOBAL":
            return {"allowed": True, "reason": "RESIDENCY_MATCHED_OR_ALLOWED"}
        else:
            return {
                "allowed": False,
                "reason": "DATA_RESIDENCY_VIOLATION",
                "resource_residency": res_upper,
                "execution_region": exec_upper,
            }

    def apply_legal_hold(
        self,
        resource_type: str,
        resource_id: str,
        case_reference: str,
        matter_name: str,
        custodian: str,
        reason: str,
        applied_by: str = "legal-admin",
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Apply active legal hold to prevent deletion or destructive anonymization."""
        hold_id = str(uuid.uuid4())
        rec = {
            "hold_id": hold_id,
            "tenant_id": tenant_id,
            "resource_type": resource_type.upper(),
            "resource_id": resource_id,
            "case_reference": case_reference,
            "matter_name": matter_name,
            "custodian": custodian,
            "reason": reason,
            "active_status": True,
            "applied_at": "2026-09-18T20:00:00Z",
            "applied_by": applied_by,
        }
        self._legal_holds[f"{resource_type.upper()}:{resource_id}"] = rec
        return rec

    def release_legal_hold(self, resource_type: str, resource_id: str, released_by: str = "legal-admin") -> bool:
        """Release active legal hold."""
        key = f"{resource_type.upper()}:{resource_id}"
        rec = self._legal_holds.get(key)
        if rec and rec["active_status"]:
            rec["active_status"] = False
            rec["released_by"] = released_by
            return True
        return False

    def evaluate_retention_action_eligibility(
        self,
        resource_type: str,
        resource_id: str,
        retention_days: int,
        creation_days_ago: int,
    ) -> Dict[str, Any]:
        """Evaluate if resource is eligible for retention cleanup or blocked by legal hold."""
        key = f"{resource_type.upper()}:{resource_id}"
        hold = self._legal_holds.get(key)

        if hold and hold["active_status"]:
            return {
                "eligible_for_deletion": False,
                "reason": "BLOCKED_BY_ACTIVE_LEGAL_HOLD",
                "hold_details": hold,
            }

        if creation_days_ago >= retention_days:
            return {
                "eligible_for_deletion": True,
                "reason": "RETENTION_EXPIRED",
                "days_exceeded": creation_days_ago - retention_days,
            }

        return {
            "eligible_for_deletion": False,
            "reason": "RETENTION_PERIOD_ACTIVE",
            "days_remaining": retention_days - creation_days_ago,
        }
