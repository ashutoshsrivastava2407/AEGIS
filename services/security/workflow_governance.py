"""Integration Bridge binding Step 9 Workflows and Step 8 Actions to Step 10 Policy Governance."""

from typing import Dict, Any, List, Optional
from services.security.policy_engine import ServerPolicyEngine
from services.workflows.services import WorkflowPlatformService


class WorkflowGovernanceBridge:
    """Integrates workflow creation, activation, and action node execution into central Step 10 policy engine."""

    def __init__(self):
        self.policy_engine = ServerPolicyEngine()
        self.workflow_service = WorkflowPlatformService()

    def evaluate_workflow_execution_policy(
        self,
        workflow_id: str,
        user_id: str,
        trigger_payload: Dict[str, Any],
        user_role: str = "WORKFLOW_OPERATOR",
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Evaluate central policy before triggering workflow execution."""
        risk_level = trigger_payload.get("risk_level", "MEDIUM")
        data_classification = trigger_payload.get("classification", "INTERNAL")

        policy_result = self.policy_engine.evaluate_policy(
            subject_id=user_id,
            resource_id=f"workflow:{workflow_id}",
            action="EXECUTE",
            context={
                "user_role": user_role,
                "risk_level": risk_level,
                "data_classification": data_classification,
            },
            tenant_id=tenant_id,
        )

        return policy_result
