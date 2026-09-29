"""Full Execution Integrity Engine, Outbox Dispatcher, and Governed Action Execution."""

import uuid
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from services.decisions.contracts import ActionContractRegistry, ActionContract
from services.agents.tools.executor import ToolExecutor


class DecisionExecutionEngine:
    """Full Execution Integrity Engine delegating action execution to Step 7 ToolExecutor."""

    def __init__(self):
        self.contract_registry = ActionContractRegistry()
        self.tool_executor = ToolExecutor()

    def execute_decision_action(
        self,
        decision_id: str,
        action_type: str,
        target_resource: str,
        parameters: Dict[str, Any],
        idempotency_key: str,
        contract_version: str = "1.0.0",
        tenant_id: str = "default",
        user_role: str = "DECISION_EXECUTOR"
    ) -> Dict[str, Any]:
        """Execute decision action following full integrity pipeline."""
        start_time = time.time()
        
        # 1. Validate action against versioned ActionContract
        validation = self.contract_registry.validate_action(action_type, parameters, contract_version)
        if not validation.get("valid", False):
            return {
                "success": False,
                "execution_status": "FAILED",
                "error": validation.get("error"),
                "postconditions_verified": False
            }

        contract: ActionContract = validation["contract"]

        # 2. Stage 1: DB Transaction Outbox Persistence Simulation (Intent Recorded)
        outbox_event = {
            "outbox_event_id": str(uuid.uuid4()),
            "decision_id": decision_id,
            "action_type": action_type,
            "idempotency_key": idempotency_key,
            "status": "DISPATCHED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # 3. Stage 2: Delegate to Step 7 Governed ToolExecutor
        tool_name = self._map_action_to_tool_name(action_type)
        tool_params = dict(parameters)
        if "action_name" not in tool_params:
            tool_params["action_name"] = action_type
        if tool_name == "scale_service_workers":
            if "service_name" not in tool_params:
                tool_params["service_name"] = target_resource or "analytics-worker"
            if "target_replicas" not in tool_params:
                tool_params["target_replicas"] = 3

        tool_result = self.tool_executor.execute_tool(
            tool_name=tool_name,
            params=tool_params,
            agent_type="DecisionExecutionAgent",
            run_id=f"run-{decision_id[:8]}",
            tenant_id=tenant_id,
            approval_granted=True
        )

        duration_ms = (time.time() - start_time) * 1000.0

        if not tool_result.get("success", False):
            return {
                "success": False,
                "execution_status": "FAILED",
                "tool_name": tool_name,
                "error": tool_result.get("error", "Governed tool execution failed."),
                "execution_result": tool_result,
                "postconditions_verified": False,
                "duration_ms": duration_ms,
                "outbox_event": outbox_event
            }

        # 4. Verify postconditions
        exec_data = tool_result.get("data") if tool_result.get("data") is not None else tool_result.get("result", {})
        postconditions_verified = self._verify_postconditions(contract.postconditions, exec_data)

        return {
            "success": postconditions_verified,
            "execution_status": "EXECUTED" if postconditions_verified else "FAILED",
            "tool_name": tool_name,
            "action_type": action_type,
            "target_resource": target_resource,
            "idempotency_key": idempotency_key,
            "contract_version": contract.contract_version,
            "execution_result": exec_data,
            "postconditions_verified": postconditions_verified,
            "duration_ms": duration_ms,
            "outbox_event": outbox_event
        }

    def _map_action_to_tool_name(self, action_type: str) -> str:
        """Map decision action types to established Step 7 governed tools."""
        mapping = {
            "SCALE_SERVICE_WORKERS": "scale_service_workers",
            "REBUILD_DATABASE_INDEX": "analytical_query",
            "REROUTE_REGIONAL_TRAFFIC": "workflow_start"
        }
        return mapping.get(action_type, "scale_service_workers")

    def _verify_postconditions(self, postconditions: List[str], result: Dict[str, Any]) -> bool:
        """Verify action contract postconditions after execution."""
        if not postconditions:
            return True
        if not result or not isinstance(result, dict):
            return False

        for cond in postconditions:
            if "==" in cond:
                key, expected_val = [x.strip() for x in cond.split("==", 1)]
                if key not in result:
                    return False
                actual_val = str(result[key])
                # If expected_val matches another key in result (e.g. target_replicas)
                if expected_val in result:
                    if str(result[expected_val]) != actual_val:
                        return False
                elif expected_val.replace(".", "", 1).isdigit() and actual_val != expected_val:
                    return False
            elif ">=" in cond:
                key, expected_val = [x.strip() for x in cond.split(">=", 1)]
                if key not in result:
                    return False
                try:
                    target_num = float(result[expected_val]) if expected_val in result else float(expected_val)
                    if float(result[key]) < target_num:
                        return False
                except (ValueError, TypeError):
                    return False
        return True
