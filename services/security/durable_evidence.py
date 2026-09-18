"""Durable Policy Decision Evidence Manager (Immutable Decision Tracking & Freshness Verification)."""

import hashlib
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional


class DurableEvidenceManager:
    """Manages immutable, durable historical policy decision records without chain-of-thought storage."""

    def __init__(self):
        self._decisions_db: Dict[str, Dict[str, Any]] = {}

    def record_policy_decision(
        self,
        subject_id: str,
        resource_type: str,
        resource_id: str,
        requested_action: str,
        policy_id: str,
        policy_version_id: str,
        policy_fingerprint: str,
        rbac_result: Dict[str, Any],
        abac_result: Dict[str, Any],
        risk_result: Dict[str, Any],
        final_effect: str,
        reason_codes: List[str],
        matched_rule_ids: List[str],
        evidence_references: List[str],
        tenant_id: str = "default",
        subject_type: str = "USER",
        approval_requirement: str = "NONE",
        authentication_strength: str = "NORMAL_AUTH",
        classification_context: str = "INTERNAL",
        correlation_id: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        action_id: Optional[str] = None,
        validity_duration_seconds: int = 300,
    ) -> Dict[str, Any]:
        """Record immutable, durable policy decision record."""
        evaluation_id = str(uuid.uuid4())
        now_dt = datetime.now(timezone.utc)
        evaluated_at = now_dt.isoformat()
        expiration_dt = now_dt + timedelta(seconds=validity_duration_seconds)
        decision_expiration_at = expiration_dt.isoformat()

        # Compute SHA-256 context hashes
        input_payload = f"{tenant_id}:{subject_id}:{resource_type}:{resource_id}:{requested_action}:{policy_fingerprint}"
        input_context_hash = hashlib.sha256(input_payload.encode("utf-8")).hexdigest()

        output_payload = f"{evaluation_id}:{final_effect}:{','.join(reason_codes)}:{evaluated_at}"
        output_decision_hash = hashlib.sha256(output_payload.encode("utf-8")).hexdigest()

        record = {
            "evaluation_id": evaluation_id,
            "tenant_id": tenant_id,
            "subject_id": subject_id,
            "subject_type": subject_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "requested_action": requested_action,
            "policy_id": policy_id,
            "policy_version_id": policy_version_id,
            "policy_fingerprint": policy_fingerprint,
            "rbac_result_json": rbac_result,
            "abac_result_json": abac_result,
            "risk_result_json": risk_result,
            "approval_requirement": approval_requirement,
            "authentication_strength": authentication_strength,
            "classification_context": classification_context,
            "final_effect": final_effect,
            "reason_codes_json": reason_codes,
            "matched_rule_ids_json": matched_rule_ids,
            "evidence_references_json": evidence_references,
            "evaluated_at": evaluated_at,
            "decision_expiration_at": decision_expiration_at,
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "workflow_run_id": workflow_run_id,
            "decision_id": decision_id,
            "action_id": action_id,
            "input_context_hash": input_context_hash,
            "output_decision_hash": output_decision_hash,
        }

        self._decisions_db[evaluation_id] = record
        return record

    def verify_decision_freshness(
        self,
        evaluation_id: str,
        current_policy_fingerprint: str,
        current_risk_level: str = "LOW",
    ) -> Dict[str, Any]:
        """Verify whether an evaluation is fresh or stale due to policy change, time expiration, or risk shift."""
        record = self._decisions_db.get(evaluation_id)
        if not record:
            return {"fresh": False, "reason": "EVALUATION_NOT_FOUND"}

        # 1. Expiration check
        exp_dt = datetime.fromisoformat(record["decision_expiration_at"])
        if datetime.now(timezone.utc) > exp_dt:
            return {"fresh": False, "reason": "DECISION_EXPIRED", "evaluated_at": record["evaluated_at"]}

        # 2. Policy fingerprint check
        if record["policy_fingerprint"] != current_policy_fingerprint:
            return {
                "fresh": False,
                "reason": "POLICY_VERSION_CHANGED",
                "recorded_fingerprint": record["policy_fingerprint"],
                "current_fingerprint": current_policy_fingerprint,
            }

        # 3. Risk shift check
        recorded_risk = record["risk_result_json"].get("risk_level", "LOW")
        if recorded_risk != current_risk_level and current_risk_level in {"HIGH", "CRITICAL"}:
            return {
                "fresh": False,
                "reason": "RISK_LEVEL_ELEVATED",
                "recorded_risk": recorded_risk,
                "current_risk": current_risk_level,
            }

        return {"fresh": True, "reason": "FRESH", "evaluation": record}

    def get_historical_decision(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve historical policy decision record."""
        return self._decisions_db.get(evaluation_id)
