"""Policy Simulator / What-If Impact Analysis Engine (Non-Mutating)."""

import uuid
from typing import Dict, Any, List, Optional
from services.security.policy_engine import ServerPolicyEngine


class PolicySimulator:
    """Evaluates proposed draft policy versions against historical or synthetic events without mutating state."""

    def __init__(self):
        self.engine = ServerPolicyEngine()

    def simulate_policy_impact(
        self,
        draft_policy_rules: List[Dict[str, Any]],
        sample_traffic: List[Dict[str, Any]],
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Run what-if impact simulation of proposed draft policy rules against sample events."""
        simulation_id = str(uuid.uuid4())
        total_events = len(sample_traffic)

        allowed_count = 0
        denied_count = 0
        approval_count = 0
        step_up_count = 0

        evaluations: List[Dict[str, Any]] = []

        for event in sample_traffic:
            res = self.engine.evaluate_policy(
                subject_id=event.get("subject_id", "user1"),
                resource_id=event.get("resource_id", "res1"),
                action=event.get("action", "READ"),
                context=event.get("context", {}),
                policy_rules=draft_policy_rules,
                tenant_id=tenant_id,
            )
            evaluations.append(res)
            dec = res["decision"]
            if dec == "ALLOW":
                allowed_count += 1
            elif dec == "DENY":
                denied_count += 1
            elif dec == "REQUIRE_APPROVAL":
                approval_count += 1
            elif dec == "REQUIRE_STEP_UP":
                step_up_count += 1

        return {
            "simulation_id": simulation_id,
            "tenant_id": tenant_id,
            "total_events_evaluated": total_events,
            "impact_summary": {
                "newly_allowed": allowed_count,
                "newly_blocked": denied_count,
                "approval_required": approval_count,
                "step_up_required": step_up_count,
            },
            "evaluations_sample": evaluations[:5],
            "state_modified": False,
        }
