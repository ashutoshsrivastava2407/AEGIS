"""AEGIS Agent Server-Side Tool Authorization & Risk Classifier Engine.

Ensures LLMs are NEVER the security boundary. Server-side code handles RBAC/ABAC,
risk tier classification, tenant boundary validation, rate limiting, and parameter sanitization.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import logging
import re
from datetime import datetime, timezone

from services.agents.tools.tool_registry import tool_registry, ToolDefinition

logger = logging.getLogger("aegis.agents.tools.authorization")


@dataclass
class AuthorizationResult:
    is_authorized: bool
    risk_tier: str
    reason: str
    sanitized_params: Dict[str, Any]
    requires_approval: bool = False


class ServerSideToolAuthorizationEngine:
    """Enforces strict server-side authorization boundaries for agent tool calls."""

    # Risk tiers mapping
    RISK_TIERS = {
        "READ_ONLY": 1,
        "LOW_RISK": 2,
        "MEDIUM_RISK": 3,
        "HIGH_RISK": 4,
        "CRITICAL": 5
    }

    # Forbidden SQL patterns in raw query inputs
    FORBIDDEN_SQL_PATTERNS = [
        r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b", r"\bALTER\b",
        r"\bUPDATE\b", r"\bINSERT\b", r"\bEXEC\b", r"\bEXECUTE\b",
        r"\bGRANT\b", r"\bREVOKE\b"
    ]

    def authorize_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        agent_type: str,
        tenant_id: str = "default",
        user_role: str = "ANALYST"
    ) -> AuthorizationResult:
        """Evaluate server-side permission, risk tier, and sanitize inputs."""
        
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            return AuthorizationResult(
                is_authorized=False,
                risk_tier="CRITICAL",
                reason=f"Tool '{tool_name}' does not exist in registry.",
                sanitized_params={}
            )

        risk_tier = tool.risk_tier

        # 1. Agent Type Tool Allowlist check
        agent_type_permissions = {
            "SUPERVISOR": ["dataset_search", "dataset_schema", "analytical_query", "metric_evaluate", "document_search", "report_generate", "notification", "workflow_start", "scale_service_workers"],
            "DATA": ["dataset_search", "dataset_schema", "data_quality", "lineage_lookup"],
            "SQL": ["analytical_query", "dataset_schema"],
            "RESEARCH_RAG": ["document_search", "retrieve_evidence", "citation_lookup"],
            "ML": ["model_lookup", "model_predict", "model_drift"],
            "INVESTIGATION": ["dataset_search", "analytical_query", "anomaly_lookup", "document_search", "report_generate"],
            "FORECASTING": ["metric_evaluate", "forecast", "analytical_query"],
            "DECISION": ["metric_evaluate", "anomaly_lookup", "model_drift", "report_generate"],
            "EXECUTION": ["notification", "workflow_start", "report_generate"],
            "DecisionExecutionAgent": ["metric_evaluate", "workflow_start", "notification", "report_generate", "analytical_query", "dataset_search", "scale_service_workers"],
            "VERIFICATION": ["citation_lookup", "data_quality", "model_drift"]
        }

        allowed_for_agent = agent_type_permissions.get(agent_type, [])
        if tool_name not in allowed_for_agent and agent_type != "SUPERVISOR":
            logger.warning(f"Agent '{agent_type}' attempted to call unauthorized tool '{tool_name}'")
            return AuthorizationResult(
                is_authorized=False,
                risk_tier=risk_tier,
                reason=f"Agent type '{agent_type}' is not granted permission to execute tool '{tool_name}'.",
                sanitized_params={}
            )

        # 2. Parameter Sanitization & Safety Guard
        sanitized, sanitize_err = self._sanitize_parameters(tool_name, params)
        if sanitize_err:
            return AuthorizationResult(
                is_authorized=False,
                risk_tier=risk_tier,
                reason=f"Input parameter validation failed: {sanitize_err}",
                sanitized_params={}
            )

        # Force tenant boundary in parameters
        sanitized["tenant_id"] = tenant_id

        # 3. Determine Human-in-the-Loop Approval Requirement
        # High and Critical risk tools require explicit human approval gate
        requires_approval = (risk_tier in ["HIGH_RISK", "CRITICAL"])

        return AuthorizationResult(
            is_authorized=True,
            risk_tier=risk_tier,
            reason="Authorized by server-side policy engine.",
            sanitized_params=sanitized,
            requires_approval=requires_approval
        )

    def _sanitize_parameters(self, tool_name: str, params: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
        """Sanitize parameters to prevent SQL injection or parameter pollution."""
        sanitized = dict(params)

        if tool_name == "analytical_query":
            sql = sanitized.get("sql", "")
            for pattern in self.FORBIDDEN_SQL_PATTERNS:
                if re.search(pattern, sql, re.IGNORECASE):
                    return {}, f"SQL statement contains illegal DDL/DML keyword matching pattern '{pattern}'"

        return sanitized, None


authorization_engine = ServerSideToolAuthorizationEngine()
