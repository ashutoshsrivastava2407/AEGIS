"""AEGIS Agent Governed Tool Registry.

Catalog of enterprise tools wrapping AEGIS Data, Analytics, ML, Knowledge, RAG, LLM, and Streaming services.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import logging

logger = logging.getLogger("aegis.agents.tools.registry")


@dataclass
class ToolDefinition:
    """Definition of a governed AEGIS tool."""
    tool_name: str
    category: str  # DATA_PLATFORM, ANALYTICS, ML_PLATFORM, KNOWLEDGE_RAG, STREAMING, WORKFLOW, NOTIFICATION
    description: str
    risk_tier: str  # READ_ONLY, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL
    schema_json: Dict[str, Any]
    handler: Optional[Callable[..., Any]] = None
    is_governed: bool = True
    rate_limit_per_min: int = 60


class ToolRegistry:
    """Central registry of all executable tools for AEGIS agents."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register_tool(self, tool: ToolDefinition) -> None:
        self._tools[tool.tool_name] = tool
        logger.debug(f"Registered tool '{tool.tool_name}' in category '{tool.category}'")

    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        return self._tools.get(tool_name)

    def list_tools(self, category: Optional[str] = None, risk_tier: Optional[str] = None) -> List[ToolDefinition]:
        result = list(self._tools.values())
        if category:
            result = [t for t in result if t.category == category]
        if risk_tier:
            result = [t for t in result if t.risk_tier == risk_tier]
        return result

    def _register_default_tools(self) -> None:
        """Register default suite of 17 AEGIS platform tools."""
        
        # 1. Data Platform Tools
        self.register_tool(ToolDefinition(
            tool_name="dataset_search",
            category="DATA_PLATFORM",
            description="Search analytical and relational datasets by keyword or domain",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term or tag"},
                    "tenant_id": {"type": "string", "description": "Tenant ID"}
                },
                "required": ["query"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="dataset_schema",
            category="DATA_PLATFORM",
            description="Retrieve structural schema and column metadata for a dataset",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Target dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="data_quality",
            category="DATA_PLATFORM",
            description="Retrieve data quality test results and compliance scores",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"}
                },
                "required": ["dataset_id"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="lineage_lookup",
            category="DATA_PLATFORM",
            description="Inspect upstream and downstream data dependencies for an asset",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string", "description": "Asset ID to trace"}
                },
                "required": ["asset_id"]
            }
        ))

        # 2. Analytics Platform Tools
        self.register_tool(ToolDefinition(
            tool_name="analytical_query",
            category="ANALYTICS",
            description="Execute read-only SQL query subject to AST security validation and row limits",
            risk_tier="LOW_RISK",
            schema_json={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL query to execute"},
                    "tenant_id": {"type": "string", "description": "Tenant context"}
                },
                "required": ["sql"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="metric_evaluate",
            category="ANALYTICS",
            description="Evaluate an enterprise KPI/metric over a specified time interval",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "metric_name": {"type": "string", "description": "Metric name"},
                    "time_window": {"type": "string", "description": "Window format (e.g. 7d, 30d)"}
                },
                "required": ["metric_name"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="anomaly_lookup",
            category="ANALYTICS",
            description="Query recent statistical metric anomalies, z-scores, and severity levels",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "metric_id": {"type": "string", "description": "Metric ID"},
                    "min_severity": {"type": "string", "description": "Severity threshold"}
                }
            }
        ))

        # 3. Knowledge & RAG Tools
        self.register_tool(ToolDefinition(
            tool_name="document_search",
            category="KNOWLEDGE_RAG",
            description="Execute hybrid vector + lexical search across enterprise knowledge bases",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query text"},
                    "collection": {"type": "string", "description": "Collection scope"},
                    "top_k": {"type": "integer", "description": "Max documents to return"}
                },
                "required": ["query"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="retrieve_evidence",
            category="KNOWLEDGE_RAG",
            description="Extract verified document chunks with complete provenance metadata",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "document_ids": {"type": "array", "items": {"type": "string"}},
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="citation_lookup",
            category="KNOWLEDGE_RAG",
            description="Verify claim against document evidence citations and calculate groundedness",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "source_chunk_ids": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["claim"]
            }
        ))

        # 4. ML Platform Tools
        self.register_tool(ToolDefinition(
            tool_name="model_lookup",
            category="ML_PLATFORM",
            description="Search registered machine learning models, versions, and deployment statuses",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "Model name"}
                }
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="model_predict",
            category="ML_PLATFORM",
            description="Invoke a registered ML model endpoint for inference scoring",
            risk_tier="LOW_RISK",
            schema_json={
                "type": "object",
                "properties": {
                    "model_id": {"type": "string", "description": "Model ID"},
                    "features_json": {"type": "object", "description": "Feature vector inputs"}
                },
                "required": ["model_id", "features_json"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="model_drift",
            category="ML_PLATFORM",
            description="Check feature and concept drift metrics (PSI) for an active model deployment",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "deployment_id": {"type": "string", "description": "Deployment ID"}
                },
                "required": ["deployment_id"]
            }
        ))

        # 5. Specialized Operational Tools
        self.register_tool(ToolDefinition(
            tool_name="forecast",
            category="ANALYTICS",
            description="Generate time-series predictions with confidence intervals for operational metrics",
            risk_tier="READ_ONLY",
            schema_json={
                "type": "object",
                "properties": {
                    "metric_name": {"type": "string"},
                    "horizon_periods": {"type": "integer", "description": "Periods ahead to forecast"}
                },
                "required": ["metric_name"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="notification",
            category="NOTIFICATION",
            description="Send structured alert notification to operational channels",
            risk_tier="MEDIUM_RISK",
            schema_json={
                "type": "object",
                "properties": {
                    "recipient": {"type": "string"},
                    "channel": {"type": "string"},
                    "message": {"type": "string"},
                    "severity": {"type": "string"}
                },
                "required": ["recipient", "message"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="workflow_start",
            category="WORKFLOW",
            description="Trigger an automated enterprise remediation workflow",
            risk_tier="HIGH_RISK",
            schema_json={
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string"},
                    "parameters": {"type": "object"}
                },
                "required": ["workflow_name"]
            }
        ))

        self.register_tool(ToolDefinition(
            tool_name="report_generate",
            category="WORKFLOW",
            description="Compile multi-agent evidence into a formal executive incident or intelligence report",
            risk_tier="LOW_RISK",
            schema_json={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "findings": {"type": "array", "items": {"type": "string"}},
                    "recommendations": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "findings"]
            }
        ))


        self.register_tool(ToolDefinition(
            tool_name="scale_service_workers",
            category="WORKFLOW",
            description="Dynamically scale service worker replicas for analytics and decision execution",
            risk_tier="MEDIUM_RISK",
            schema_json={
                "type": "object",
                "properties": {
                    "service_name": {"type": "string"},
                    "target_replicas": {"type": "integer"}
                },
                "required": ["service_name", "target_replicas"]
            }
        ))


tool_registry = ToolRegistry()
