"""Agent Permission Boundary, Tool Allowlist, and Oversight Governance Manager."""

from typing import Dict, Any, List, Optional


class AgentGovernanceManager:
    """Enforces agent-specific permission boundaries, tool allowlists, and risk ceilings."""

    def validate_agent_tool_execution(
        self,
        agent_type: str,
        tool_name: str,
        tool_params: Dict[str, Any],
        agent_risk_ceiling: str = "HIGH_RISK",
        allowed_tools: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Validate agent tool invocation against explicit agent permission boundary (Not inherited from human creator)."""
        allowed = allowed_tools or ["query_analytics", "run_forecast", "scale_service_workers", "metric_evaluate", "report_generate"]

        if tool_name not in allowed:
            return {
                "permitted": False,
                "reason": f"Tool '{tool_name}' is not in agent '{agent_type}' tool allowlist {allowed}",
            }

        # Check risk ceiling
        if tool_name == "scale_service_workers" and agent_risk_ceiling == "LOW_RISK":
            return {
                "permitted": False,
                "reason": f"Tool '{tool_name}' exceeds agent risk ceiling '{agent_risk_ceiling}'",
            }

        return {"permitted": True, "reason": "Agent tool execution permitted by boundary policy."}
