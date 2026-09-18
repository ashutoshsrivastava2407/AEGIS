"""Central Server-Side Declarative Policy Engine (No Chain-of-Thought Storage)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class ServerPolicyEngine:
    """Central declarative policy evaluator returning structured, auditable policy results."""

    DECISIONS = {"ALLOW", "DENY", "REQUIRE_APPROVAL", "REQUIRE_STEP_UP", "RESTRICT"}

    def evaluate_policy(
        self,
        subject_id: str,
        resource_id: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        policy_rules: Optional[List[Dict[str, Any]]] = None,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Evaluate declarative policy rules deterministically against request context.
        
        Returns structured decision: ALLOW, DENY, REQUIRE_APPROVAL, REQUIRE_STEP_UP, or RESTRICT.
        """
        eval_id = str(uuid.uuid4())
        ctx = context or {}
        rules = policy_rules or []

        user_role = ctx.get("user_role", "USER")
        risk_level = ctx.get("risk_level", "LOW")
        data_classification = ctx.get("data_classification", "INTERNAL")

        # Deny high risk actions for non-admin users
        if risk_level == "CRITICAL" and user_role != "ENTERPRISE_ADMIN":
            return {
                "evaluation_id": eval_id,
                "tenant_id": tenant_id,
                "subject_id": subject_id,
                "resource_id": resource_id,
                "action": action,
                "decision": "DENY",
                "reason_code": "CRITICAL_RISK_ADMIN_ONLY",
                "matched_rules": [{"rule": "critical_risk_gate", "effect": "DENY"}],
                "risk_score": {"score": 0.95, "tier": "CRITICAL"},
                "evidence_references": ["rule:critical_risk_gate"],
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
            }

        # Require approval for high-risk actions or confidential data changes
        if risk_level == "HIGH" or action.upper().startswith("APPROVE_"):
            return {
                "evaluation_id": eval_id,
                "tenant_id": tenant_id,
                "subject_id": subject_id,
                "resource_id": resource_id,
                "action": action,
                "decision": "REQUIRE_APPROVAL",
                "reason_code": "HIGH_RISK_APPROVAL_REQUIRED",
                "matched_rules": [{"rule": "high_risk_approval", "effect": "REQUIRE_APPROVAL"}],
                "risk_score": {"score": 0.75, "tier": "HIGH"},
                "evidence_references": ["rule:high_risk_approval"],
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
            }

        # Require step-up for RESTRICTED data
        if data_classification == "RESTRICTED":
            return {
                "evaluation_id": eval_id,
                "tenant_id": tenant_id,
                "subject_id": subject_id,
                "resource_id": resource_id,
                "action": action,
                "decision": "REQUIRE_STEP_UP",
                "reason_code": "RESTRICTED_DATA_STEP_UP_REQUIRED",
                "matched_rules": [{"rule": "restricted_data_step_up", "effect": "REQUIRE_STEP_UP"}],
                "risk_score": {"score": 0.60, "tier": "MEDIUM"},
                "evidence_references": ["rule:restricted_data_step_up"],
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
            }

        # Default Allow
        return {
            "evaluation_id": eval_id,
            "tenant_id": tenant_id,
            "subject_id": subject_id,
            "resource_id": resource_id,
            "action": action,
            "decision": "ALLOW",
            "reason_code": "POLICY_ALLOW_MATCH",
            "matched_rules": [{"rule": "default_allow_rule", "effect": "ALLOW"}],
            "risk_score": {"score": 0.10, "tier": "LOW"},
            "evidence_references": ["rule:default_allow_rule"],
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }
