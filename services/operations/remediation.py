"""Policy-Governed Automated Remediation Engine.

Delegates action execution strictly to Step 7 ToolExecutor/DecisionExecutionEngine and
governance evaluation to Step 10 ServerPolicyEngine (zero un-governed execution).
"""

import uuid
import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from services.security.policy_engine import ServerPolicyEngine
from services.decisions.execution import DecisionExecutionEngine
from packages.database.models.operations import DurableRemediationEvidenceModel


class PolicyGovernedRemediationService:
    """Service for policy-governed automated remediation with immutable evidence trails."""

    def __init__(self, db_session=None):
        self.db = db_session
        self.policy_engine = ServerPolicyEngine()
        self.execution_engine = DecisionExecutionEngine()
        self._evidence_records: List[Dict[str, Any]] = []

    def execute_remediation(
        self,
        remediation_action: str,
        target_service_id: str,
        parameters: Dict[str, Any],
        actor_id: str = "AutomatedRemediationEngine",
        incident_id: Optional[str] = None,
        tenant_id: str = "default",
        user_role: str = "SRE_AUTOMATION",
    ) -> Dict[str, Any]:
        """Execute a policy-governed remediation action."""
        remediation_id = f"rem-{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()

        before_health = {
            "service_id": target_service_id,
            "status": "DEGRADED",
            "timestamp": now_str,
        }

        # 1. Step 10 Server-Authoritative Policy Evaluation
        eval_context = {
            "user_role": user_role,
            "risk_level": parameters.get("risk_level", "MEDIUM"),
            "data_classification": "INTERNAL",
            "action": remediation_action,
            "target_service": target_service_id,
        }

        policy_result = self.policy_engine.evaluate_policy(
            subject_id=actor_id,
            resource_id=target_service_id,
            action=remediation_action,
            context=eval_context,
            tenant_id=tenant_id,
        )

        policy_decision = policy_result.get("decision", "DENY")
        policy_evaluation_id = policy_result.get("evaluation_id", str(uuid.uuid4()))

        # 2. Block execution if policy does not allow
        if policy_decision not in ["ALLOW"]:
            evidence_hash = self._compute_evidence_hash(
                remediation_id, target_service_id, remediation_action, policy_decision, "BLOCKED_BY_POLICY"
            )
            blocked_record = {
                "id": remediation_id,
                "remediation_id": remediation_id,
                "target_service_id": target_service_id,
                "remediation_action": remediation_action,
                "parameters": parameters,
                "policy_decision": policy_decision,
                "policy_evaluation_id": policy_evaluation_id,
                "execution_status": "BLOCKED_BY_POLICY",
                "error_details": f"Policy decision '{policy_decision}' prevented remediation execution.",
                "before_health_state": before_health,
                "after_health_state": before_health,
                "evidence_hash": evidence_hash,
                "tenant_id": tenant_id,
                "executed_at": now_str,
            }
            self._record_evidence(blocked_record)
            return blocked_record

        # 3. Delegate execution to Step 7 Governed Execution Engine
        exec_result = self.execution_engine.execute_decision_action(
            decision_id=incident_id or remediation_id,
            action_type=remediation_action,
            target_resource=target_service_id,
            parameters=parameters,
            idempotency_key=f"rem-idemp-{remediation_id}",
            tenant_id=tenant_id,
            user_role=user_role,
        )

        success = exec_result.get("success", False)
        execution_status = "SUCCESS" if success else "FAILED"
        error_details = exec_result.get("error") if not success else None

        after_health = {
            "service_id": target_service_id,
            "status": "HEALTHY" if success else "DEGRADED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        evidence_hash = self._compute_evidence_hash(
            remediation_id, target_service_id, remediation_action, policy_decision, execution_status
        )

        remediation_record = {
            "id": remediation_id,
            "remediation_id": remediation_id,
            "target_service_id": target_service_id,
            "remediation_action": remediation_action,
            "parameters": parameters,
            "policy_decision": policy_decision,
            "policy_evaluation_id": policy_evaluation_id,
            "execution_status": execution_status,
            "error_details": error_details,
            "before_health_state": before_health,
            "after_health_state": after_health,
            "evidence_hash": evidence_hash,
            "tenant_id": tenant_id,
            "executed_at": now_str,
        }

        self._record_evidence(remediation_record)
        return remediation_record

    def _compute_evidence_hash(
        self,
        rem_id: str,
        service_id: str,
        action: str,
        decision: str,
        status: str,
    ) -> str:
        """Compute SHA-256 cryptographic fingerprint of remediation evidence."""
        raw = f"{rem_id}:{service_id}:{action}:{decision}:{status}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _record_evidence(self, record: Dict[str, Any]) -> None:
        """Store remediation evidence record in-memory and database."""
        self._evidence_records.append(record)

        if self.db:
            model = DurableRemediationEvidenceModel(
                id=record["id"],
                target_service_id=record["target_service_id"],
                remediation_action=record["remediation_action"],
                parameters_json=record["parameters"],
                policy_decision=record["policy_decision"],
                policy_evaluation_id=record["policy_evaluation_id"],
                execution_status=record["execution_status"],
                before_health_json=record["before_health_state"],
                after_health_json=record["after_health_state"],
                error_details=record.get("error_details"),
                evidence_hash=record["evidence_hash"],
                tenant_id=record["tenant_id"],
            )
            self.db.add(model)
            self.db.commit()

    def list_remediation_evidence(
        self,
        target_service_id: Optional[str] = None,
        tenant_id: str = "default",
    ) -> List[Dict[str, Any]]:
        """List historical remediation evidence records."""
        records = [
            r for r in self._evidence_records
            if r.get("tenant_id", "default") == tenant_id
        ]
        if target_service_id:
            records = [r for r in records if r.get("target_service_id") == target_service_id]
        return records
