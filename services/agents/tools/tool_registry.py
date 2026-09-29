"""AEGIS Agent Governed Tool Registry.

Catalog of enterprise tools wrapping AEGIS Data, Analytics, ML, Knowledge, RAG, LLM, Decision, Policy, and Workflow platform services.
Provides typed input, output, and error schemas with native LLM provider export formats (OpenAI, Anthropic, Gemini).
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import logging
import uuid

logger = logging.getLogger("aegis.agents.tools.registry")


@dataclass
class ToolDefinition:
    """Production-grade definition of a governed AEGIS tool."""

    tool_name: str
    category: str  # DATA_PLATFORM, ANALYTICS, ML_PLATFORM, KNOWLEDGE_RAG, INTELLIGENCE, DECISION_INTELLIGENCE, WORKFLOW_ACTION, NOTIFICATION
    description: str
    risk_tier: str  # READ_ONLY, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any] = field(default_factory=dict)
    error_schema: Dict[str, Any] = field(default_factory=dict)
    tool_id: str = field(default="")
    version: str = "1.0.0"
    required_capabilities: List[str] = field(default_factory=lambda: ["EXECUTE"])
    allowed_data_classifications: List[str] = field(default_factory=lambda: ["PUBLIC", "INTERNAL", "RESTRICTED"])
    tenant_scope: str = "GLOBAL"
    execution_timeout: int = 30
    idempotency_behavior: str = "IDEMPOTENT"  # IDEMPOTENT, NON_IDEMPOTENT, STRICT
    approval_requirement: str = "NONE"  # NONE, OPTIONAL, MANDATORY
    enabled: bool = True
    handler: Optional[Callable[..., Any]] = None
    is_governed: bool = True
    rate_limit_per_min: int = 60

    def __post_init__(self):
        if not self.tool_id:
            self.tool_id = f"tool_{self.tool_name}"
        if not self.output_schema:
            self.output_schema = {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "data": {"type": "object"}
                },
                "required": ["status"]
            }
        if not self.error_schema:
            self.error_schema = {
                "type": "object",
                "properties": {
                    "error_code": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["error_code", "message"]
            }

    @property
    def schema_json(self) -> Dict[str, Any]:
        """Backward-compatible property returning input_schema."""
        return self.input_schema

    def to_openai_tool_schema(self) -> Dict[str, Any]:
        """Export tool definition in OpenAI function-calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }

    def to_anthropic_tool_schema(self) -> Dict[str, Any]:
        """Export tool definition in Anthropic tool-use format."""
        return {
            "name": self.tool_name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def to_gemini_tool_schema(self) -> Dict[str, Any]:
        """Export tool definition in Gemini function declarations format."""
        return {
            "name": self.tool_name,
            "description": self.description,
            "parameters": self.input_schema,
        }


class ToolRegistry:
    """Central registry of all executable governed tools for AEGIS agents."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register_tool(self, tool: ToolDefinition) -> None:
        self._tools[tool.tool_name] = tool
        logger.debug(f"Registered tool '{tool.tool_name}' in category '{tool.category}'")

    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        return self._tools.get(tool_name)

    def list_tools(
        self,
        category: Optional[str] = None,
        risk_tier: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[ToolDefinition]:
        result = list(self._tools.values())
        if enabled_only:
            result = [t for t in result if t.enabled]
        if category:
            result = [t for t in result if t.category == category]
        if risk_tier:
            result = [t for t in result if t.risk_tier == risk_tier]
        return result

    def export_tools_schema(self, provider_format: str = "openai") -> List[Dict[str, Any]]:
        """Export all registered enabled tools in specified LLM provider format."""
        tools = self.list_tools(enabled_only=True)
        if provider_format.lower() == "anthropic":
            return [t.to_anthropic_tool_schema() for t in tools]
        elif provider_format.lower() == "gemini":
            return [t.to_gemini_tool_schema() for t in tools]
        else:
            return [t.to_openai_tool_schema() for t in tools]

    def _register_default_tools(self) -> None:
        """Register the core 18 AEGIS platform governed tools with typed schemas."""

        # 1. DATA: query_analytics
        self.register_tool(ToolDefinition(
            tool_name="query_analytics",
            category="DATA_PLATFORM",
            description="Execute AST-validated read-only analytical SQL query against data lake datasets",
            risk_tier="LOW_RISK",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "Read-only SQL query"},
                    "limit": {"type": "integer", "description": "Row limit constraint", "default": 100}
                },
                "required": ["sql"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "sql_text": {"type": "string"},
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "rows": {"type": "array"},
                    "row_count": {"type": "integer"}
                },
                "required": ["status", "columns", "rows"]
            }
        ))

        # 2. DATA: get_dataset_metadata
        self.register_tool(ToolDefinition(
            tool_name="get_dataset_metadata",
            category="DATA_PLATFORM",
            description="Retrieve structural schema, layer tags, and column metadata for a target dataset",
            risk_tier="READ_ONLY",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Target dataset ID"}
                },
                "required": ["dataset_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string"},
                    "columns": {"type": "array"}
                },
                "required": ["dataset_id", "columns"]
            }
        ))

        # 3. DATA: get_data_quality
        self.register_tool(ToolDefinition(
            tool_name="get_data_quality",
            category="DATA_PLATFORM",
            description="Retrieve data quality test results, compliance scores, and validation reports",
            risk_tier="READ_ONLY",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset identifier"}
                },
                "required": ["dataset_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string"},
                    "overall_score": {"type": "number"},
                    "status": {"type": "string"}
                },
                "required": ["dataset_id", "overall_score", "status"]
            }
        ))

        # 4. DATA: get_lineage
        self.register_tool(ToolDefinition(
            tool_name="get_lineage",
            category="DATA_PLATFORM",
            description="Inspect upstream and downstream data dependency graphs for an enterprise asset",
            risk_tier="READ_ONLY",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string", "description": "Asset or dataset ID"}
                },
                "required": ["asset_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string"},
                    "upstream_nodes": {"type": "array"},
                    "downstream_nodes": {"type": "array"}
                },
                "required": ["asset_id"]
            }
        ))

        # 5. KNOWLEDGE: search_knowledge
        self.register_tool(ToolDefinition(
            tool_name="search_knowledge",
            category="KNOWLEDGE_RAG",
            description="Execute hybrid vector + keyword search across enterprise knowledge collections",
            risk_tier="READ_ONLY",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query text"},
                    "top_k": {"type": "integer", "description": "Max items to retrieve", "default": 5}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "chunks_count": {"type": "integer"},
                    "chunks": {"type": "array"}
                },
                "required": ["query", "chunks"]
            }
        ))

        # 6. KNOWLEDGE: retrieve_evidence
        self.register_tool(ToolDefinition(
            tool_name="retrieve_evidence",
            category="KNOWLEDGE_RAG",
            description="Extract verified document evidence chunks with complete provenance metadata",
            risk_tier="READ_ONLY",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Evidence topic query"}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "evidence_chunks": {"type": "array"}
                },
                "required": ["query", "evidence_chunks"]
            }
        ))

        # 7. ML: run_ml_inference
        self.register_tool(ToolDefinition(
            tool_name="run_ml_inference",
            category="ML_PLATFORM",
            description="Invoke a registered ML model endpoint for inference scoring",
            risk_tier="MEDIUM_RISK",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "model_id": {"type": "string", "description": "Model ID"},
                    "features_json": {"type": "object", "description": "Input feature payload"}
                },
                "required": ["model_id", "features_json"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "model_id": {"type": "string"},
                    "prediction": {"type": "array"},
                    "status": {"type": "string"}
                },
                "required": ["model_id", "prediction", "status"]
            }
        ))

        # 8. ML: get_model_metadata
        self.register_tool(ToolDefinition(
            tool_name="get_model_metadata",
            category="ML_PLATFORM",
            description="Search registered machine learning models, versions, and deployment statuses",
            risk_tier="READ_ONLY",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "Model name"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "models": {"type": "array"}
                },
                "required": ["models"]
            }
        ))

        # 9. ML: get_model_drift
        self.register_tool(ToolDefinition(
            tool_name="get_model_drift",
            category="ML_PLATFORM",
            description="Check feature and concept drift metrics (PSI) for active model deployment",
            risk_tier="READ_ONLY",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "deployment_id": {"type": "string", "description": "Deployment ID"}
                },
                "required": ["deployment_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "deployment_id": {"type": "string"},
                    "psi_value": {"type": "number"},
                    "drift_detected": {"type": "boolean"}
                },
                "required": ["deployment_id", "psi_value", "drift_detected"]
            }
        ))

        # 10. INTELLIGENCE: investigate_anomaly
        self.register_tool(ToolDefinition(
            tool_name="investigate_anomaly",
            category="INTELLIGENCE",
            description="Query recent statistical metric anomalies, z-scores, and severity levels",
            risk_tier="READ_ONLY",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "metric_id": {"type": "string", "description": "Target metric ID"},
                    "min_severity": {"type": "string", "description": "Severity threshold", "default": "MEDIUM"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "metric_id": {"type": "string"},
                    "anomalies_count": {"type": "integer"},
                    "anomalies": {"type": "array"}
                },
                "required": ["metric_id", "anomalies"]
            }
        ))

        # 11. INTELLIGENCE: forecast_metric
        self.register_tool(ToolDefinition(
            tool_name="forecast_metric",
            category="INTELLIGENCE",
            description="Generate time-series predictions with confidence intervals for operational metrics",
            risk_tier="MEDIUM_RISK",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "metric_name": {"type": "string", "description": "Target metric name"},
                    "horizon_periods": {"type": "integer", "description": "Periods ahead to forecast", "default": 7}
                },
                "required": ["metric_name"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "metric_name": {"type": "string"},
                    "horizon_periods": {"type": "integer"},
                    "forecast_points": {"type": "array"}
                },
                "required": ["metric_name", "forecast_points"]
            }
        ))

        # 12. DECISION INTELLIGENCE: simulate_decision
        self.register_tool(ToolDefinition(
            tool_name="simulate_decision",
            category="DECISION_INTELLIGENCE",
            description="Run stochastic scenario simulations for candidate decision options",
            risk_tier="MEDIUM_RISK",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "decision_topic": {"type": "string", "description": "Topic or context of decision"},
                    "options": {"type": "array", "items": {"type": "string"}, "description": "Candidate options"}
                },
                "required": ["decision_topic"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "decision_topic": {"type": "string"},
                    "simulated_scenarios": {"type": "array"},
                    "optimal_option": {"type": "string"}
                },
                "required": ["decision_topic", "simulated_scenarios"]
            }
        ))

        # 13. DECISION INTELLIGENCE: evaluate_policy
        self.register_tool(ToolDefinition(
            tool_name="evaluate_policy",
            category="DECISION_INTELLIGENCE",
            description="Evaluate candidate action against server-authoritative security & business policies",
            risk_tier="LOW_RISK",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "action_name": {"type": "string", "description": "Target action name"},
                    "context_params": {"type": "object", "description": "Evaluation context"}
                },
                "required": ["action_name"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "action_name": {"type": "string"},
                    "decision": {"type": "string"},
                    "requires_approval": {"type": "boolean"}
                },
                "required": ["action_name", "decision"]
            }
        ))

        # 14. DECISION INTELLIGENCE: create_decision
        self.register_tool(ToolDefinition(
            tool_name="create_decision",
            category="DECISION_INTELLIGENCE",
            description="Formally draft a governed decision manifest with trade-off analysis and rationale",
            risk_tier="HIGH_RISK",
            approval_requirement="MANDATORY",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Decision title"},
                    "recommended_option": {"type": "string", "description": "Selected option"},
                    "rationale": {"type": "string", "description": "Justification rationale"}
                },
                "required": ["title", "recommended_option"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "decision_id": {"type": "string"},
                    "title": {"type": "string"},
                    "status": {"type": "string"}
                },
                "required": ["decision_id", "status"]
            }
        ))

        # 15. WORKFLOW / ACTION: create_approval_request
        self.register_tool(ToolDefinition(
            tool_name="create_approval_request",
            category="WORKFLOW_ACTION",
            description="Submit formal human-in-the-loop approval request for high-risk action",
            risk_tier="HIGH_RISK",
            approval_requirement="MANDATORY",
            input_schema={
                "type": "object",
                "properties": {
                    "action_type": {"type": "string", "description": "Action type to approve"},
                    "justification": {"type": "string", "description": "Business rationale"}
                },
                "required": ["action_type", "justification"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "approval_id": {"type": "string"},
                    "status": {"type": "string"}
                },
                "required": ["approval_id", "status"]
            }
        ))

        # 16. WORKFLOW / ACTION: execute_workflow
        self.register_tool(ToolDefinition(
            tool_name="execute_workflow",
            category="WORKFLOW_ACTION",
            description="Trigger an automated governed saga or remediation workflow",
            risk_tier="HIGH_RISK",
            approval_requirement="MANDATORY",
            input_schema={
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string", "description": "Workflow identifier"},
                    "parameters": {"type": "object", "description": "Workflow parameters"}
                },
                "required": ["workflow_name"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string"},
                    "status": {"type": "string"}
                },
                "required": ["workflow_id", "status"]
            }
        ))

        # 17. WORKFLOW / ACTION: execute_action
        self.register_tool(ToolDefinition(
            tool_name="execute_action",
            category="WORKFLOW_ACTION",
            description="Execute authorized operational action through Step 8 ActionContract & GovernedToolExecutor",
            risk_tier="HIGH_RISK",
            approval_requirement="MANDATORY",
            input_schema={
                "type": "object",
                "properties": {
                    "action_name": {"type": "string", "description": "Action contract name"},
                    "parameters": {"type": "object", "description": "Action parameters"}
                },
                "required": ["action_name"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "action_name": {"type": "string"},
                    "status": {"type": "string"}
                },
                "required": ["action_name", "status"]
            }
        ))

        # 18. WORKFLOW / ACTION: verify_postcondition
        self.register_tool(ToolDefinition(
            tool_name="verify_postcondition",
            category="WORKFLOW_ACTION",
            description="Verify expected post-execution state and metric stability following action execution",
            risk_tier="READ_ONLY",
            approval_requirement="NONE",
            input_schema={
                "type": "object",
                "properties": {
                    "target_identifier": {"type": "string", "description": "Target component or metric ID"},
                    "expected_condition": {"type": "string", "description": "Expected status or threshold"}
                },
                "required": ["target_identifier"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "target_identifier": {"type": "string"},
                    "verified": {"type": "boolean"},
                    "details": {"type": "string"}
                },
                "required": ["target_identifier", "verified"]
            }
        ))

        # Aliases for backwards-compatibility with Step 7 baseline tests
        self._register_aliases()

    def _register_aliases(self) -> None:
        """Map legacy tool names to the 18 primary tools to maintain 100% backward compatibility."""
        aliases = {
            "dataset_search": "get_dataset_metadata",
            "dataset_schema": "get_dataset_metadata",
            "data_quality": "get_data_quality",
            "lineage_lookup": "get_lineage",
            "analytical_query": "query_analytics",
            "metric_evaluate": "query_analytics",
            "anomaly_lookup": "investigate_anomaly",
            "document_search": "search_knowledge",
            "citation_lookup": "search_knowledge",
            "model_lookup": "get_model_metadata",
            "model_predict": "run_ml_inference",
            "model_drift": "get_model_drift",
            "forecast": "forecast_metric",
            "workflow_start": "execute_workflow",
            "scale_service_workers": "execute_action",
            "report_generate": "create_decision",
            "notification": "execute_action",
        }
        for alias_name, target_name in aliases.items():
            if alias_name not in self._tools and target_name in self._tools:
                target_tool = self._tools[target_name]
                alias_tool = ToolDefinition(
                    tool_name=alias_name,
                    category=target_tool.category,
                    description=target_tool.description,
                    risk_tier=target_tool.risk_tier,
                    input_schema=target_tool.input_schema,
                    output_schema=target_tool.output_schema,
                    error_schema=target_tool.error_schema,
                    approval_requirement=target_tool.approval_requirement,
                    handler=target_tool.handler
                )
                self.register_tool(alias_tool)


tool_registry = ToolRegistry()
