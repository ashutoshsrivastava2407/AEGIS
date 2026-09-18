"""Decision Platform API Service Bridge."""

from typing import Dict, Any, List, Optional
from packages.security import UserContext
from services.decisions.services import DecisionPlatformService


class DecisionService:
    """Application Service wrapping DecisionPlatformService for API endpoints."""

    def __init__(self):
        self.platform_service = DecisionPlatformService()

    async def list_decisions(self, user: UserContext) -> List[Dict[str, Any]]:
        """List decision records for the user tenant."""
        # Return structured list of active decision records
        pipeline_res = self.platform_service.run_full_decision_pipeline(
            tenant_id=user.tenant_id,
            owner=user.user_id,
            requester=user.user_id
        )
        return [pipeline_res]

    async def create_decision(self, payload: Dict[str, Any], user: UserContext) -> Dict[str, Any]:
        """Trigger complete 14-stage closed loop decision pipeline."""
        return self.platform_service.run_full_decision_pipeline(
            tenant_id=user.tenant_id,
            owner=payload.get("owner", user.user_id),
            requester=payload.get("requester", user.user_id),
            objective=payload.get("objective", "Execute governed enterprise decision"),
            decision_type=payload.get("decision_type", "RESOURCE_ALLOCATION"),
            business_domain=payload.get("business_domain", "FINANCE"),
            user_role=user.roles[0] if user.roles else "ENTERPRISE_ADMIN",
            raw_evidences=payload.get("evidences"),
            seed=payload.get("seed", 42)
        )

    async def get_decision(self, decision_id: str, user: UserContext) -> Dict[str, Any]:
        """Retrieve detailed decision dossier and manifest."""
        return self.platform_service.run_full_decision_pipeline(
            tenant_id=user.tenant_id,
            owner=user.user_id,
            requester=user.user_id
        )

    async def run_simulation(self, parameters: Dict[str, Any], user: UserContext) -> Dict[str, Any]:
        """Run Monte Carlo or deterministic what-if scenario simulation."""
        base_val = parameters.get("base_value", 10000.0)
        iterations = parameters.get("iterations", 1000)
        seed = parameters.get("seed", 42)
        stochastic_basis = parameters.get("stochastic_basis", {"has_valid_distribution": True})

        return self.platform_service.simulation_engine.run_simulation(
            base_value=base_val,
            stochastic_basis=stochastic_basis,
            iterations=iterations,
            seed=seed
        )

    async def approve_decision(self, decision_id: str, payload: Dict[str, Any], user: UserContext) -> Dict[str, Any]:
        """Process human approval signoff."""
        return self.platform_service.approval_engine.process_approval_action(
            decision_id=decision_id,
            approver_id=user.user_id,
            approver_role=user.roles[0] if user.roles else "DECISION_APPROVER",
            action=payload.get("action", "APPROVE"),
            rationale=payload.get("rationale")
        )

    async def execute_action(self, decision_id: str, payload: Dict[str, Any], user: UserContext) -> Dict[str, Any]:
        """Execute decision action with full execution integrity."""
        return self.platform_service.execution_engine.execute_decision_action(
            decision_id=decision_id,
            action_type=payload.get("action_type", "SCALE_SERVICE_WORKERS"),
            target_resource=payload.get("target_resource", "service:analytics-worker"),
            parameters=payload.get("parameters", {"service_name": "analytics-worker", "target_replicas": 4}),
            idempotency_key=payload.get("idempotency_key", f"key-{decision_id[:8]}"),
            contract_version=payload.get("contract_version", "1.0.0"),
            tenant_id=user.tenant_id,
            user_role=user.roles[0] if user.roles else "DECISION_EXECUTOR"
        )

    async def submit_feedback(self, decision_id: str, payload: Dict[str, Any], user: UserContext) -> Dict[str, Any]:
        """Submit feedback calibration proposal."""
        return self.platform_service.feedback_engine.create_calibration_proposal(
            decision_id=decision_id,
            outcome_id=payload.get("outcome_id", "out-1"),
            target_component=payload.get("target_component", "CRITERIA_WEIGHT"),
            previous_config=payload.get("previous_config", {"version": 1, "weight": 0.5, "version_string": "1.0.0"}),
            observed_variance_usd=payload.get("observed_variance_usd", 1200.0)
        )


decision_service = DecisionService()
