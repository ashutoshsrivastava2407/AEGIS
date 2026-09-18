"""AEGIS Agent Multi-Step DAG Planner & Task Decomposer.

Decomposes complex enterprise intelligence goals into structured Directed Acyclic Graphs (DAGs),
assigns specialized agents, resolves dependencies, and calculates risk scores.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import uuid
import logging
from datetime import datetime, timezone

from services.agents.tools.tool_registry import tool_registry

logger = logging.getLogger("aegis.agents.planning.planner")


@dataclass
class PlanNode:
    node_key: str
    task_type: str
    task_description: str
    assigned_agent_type: str
    dependencies: List[str] = field(default_factory=list)
    tool_name: Optional[str] = None
    tool_params: Dict[str, Any] = field(default_factory=dict)
    status: str = "PENDING"
    result: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    plan_id: str
    run_id: str
    goal_statement: str
    nodes: Dict[str, PlanNode] = field(default_factory=dict)
    execution_order: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    status: str = "DRAFT"


class DAGPlanner:
    """Enterprise Goal Decomposer & Plan Generator."""

    def create_plan(
        self,
        goal_statement: str,
        run_id: str,
        tenant_id: str = "default",
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """Decompose a complex enterprise query or investigation goal into a DAG plan."""
        
        plan_id = str(uuid.uuid4())
        context = context or {}

        # Rule-based or structured LLM breakdown of complex multi-agent goals
        nodes = self._decompose_goal(goal_statement, context)

        # Validate DAG & build topological execution order
        execution_order = self._topological_sort(nodes)

        # Calculate cumulative plan risk score
        risk_score = self._calculate_risk_score(nodes)

        plan = ExecutionPlan(
            plan_id=plan_id,
            run_id=run_id,
            goal_statement=goal_statement,
            nodes=nodes,
            execution_order=execution_order,
            risk_score=risk_score,
            status="APPROVED" if risk_score < 0.7 else "DRAFT"
        )

        logger.info(f"Generated plan '{plan_id}' with {len(nodes)} nodes, risk_score={risk_score:.2f}")
        return plan

    def _decompose_goal(self, goal: str, context: Dict[str, Any]) -> Dict[str, PlanNode]:
        """Decompose goal statement into a multi-agent DAG."""

        goal_lower = goal.lower()
        nodes: Dict[str, PlanNode] = {}

        # 1. Flagship Revenue / Anomaly Investigation Pipeline
        if "revenue" in goal_lower or "anomaly" in goal_lower or "drop" in goal_lower:
            nodes["step_1_detect_anomaly"] = PlanNode(
                node_key="step_1_detect_anomaly",
                task_type="ANOMALY_DETECTION",
                task_description="Search for statistical metric anomalies and z-scores in revenue metrics",
                assigned_agent_type="INVESTIGATION",
                dependencies=[],
                tool_name="anomaly_lookup",
                tool_params={"metric_id": context.get("metric_id", "m_rev_001")}
            )
            nodes["step_2_query_data"] = PlanNode(
                node_key="step_2_query_data",
                task_type="DATA_QUERY",
                task_description="Execute analytical query to segment revenue breakdown by product line and region",
                assigned_agent_type="SQL",
                dependencies=["step_1_detect_anomaly"],
                tool_name="analytical_query",
                tool_params={"sql": "SELECT region, product_line, SUM(amount) FROM revenue_tx GROUP BY region, product_line"}
            )
            nodes["step_3_search_knowledge"] = PlanNode(
                node_key="step_3_search_knowledge",
                task_type="RAG_SEARCH",
                task_description="Retrieve enterprise incident reports and market context documentation",
                assigned_agent_type="RESEARCH_RAG",
                dependencies=["step_1_detect_anomaly"],
                tool_name="document_search",
                tool_params={"query": "revenue drop incident region factors"}
            )
            nodes["step_4_check_ml_drift"] = PlanNode(
                node_key="step_4_check_ml_drift",
                task_type="ML_DRIFT_CHECK",
                task_description="Check feature drift and PSI metrics for demand forecasting model",
                assigned_agent_type="ML",
                dependencies=["step_2_query_data"],
                tool_name="model_drift",
                tool_params={"deployment_id": "dep_forecast_01"}
            )
            nodes["step_5_verify_evidence"] = PlanNode(
                node_key="step_5_verify_evidence",
                task_type="VERIFICATION",
                task_description="Verify claim citations and calculate groundedness score",
                assigned_agent_type="VERIFICATION",
                dependencies=["step_3_search_knowledge"],
                tool_name="citation_lookup",
                tool_params={"claim": "Revenue drop caused by regional outage"}
            )
            nodes["step_6_generate_report"] = PlanNode(
                node_key="step_6_generate_report",
                task_type="REPORT_GENERATION",
                task_description="Synthesize root cause analysis into an executive incident report",
                assigned_agent_type="SUPERVISOR",
                dependencies=["step_2_query_data", "step_3_search_knowledge", "step_4_check_ml_drift", "step_5_verify_evidence"],
                tool_name="report_generate",
                tool_params={"title": f"Root Cause Analysis Report: {goal}"}
            )

        # 2. General Data & Research Pipeline
        elif "research" in goal_lower or "document" in goal_lower or "find" in goal_lower:
            nodes["step_1_search"] = PlanNode(
                node_key="step_1_search",
                task_type="RAG_SEARCH",
                task_description="Execute search across enterprise knowledge repositories",
                assigned_agent_type="RESEARCH_RAG",
                dependencies=[],
                tool_name="document_search",
                tool_params={"query": goal}
            )
            nodes["step_2_evidence"] = PlanNode(
                node_key="step_2_evidence",
                task_type="EVIDENCE_EXTRACTION",
                task_description="Extract verified document chunks with provenance",
                assigned_agent_type="RESEARCH_RAG",
                dependencies=["step_1_search"],
                tool_name="retrieve_evidence",
                tool_params={"query": goal}
            )
            nodes["step_3_verify"] = PlanNode(
                node_key="step_3_verify",
                task_type="VERIFICATION",
                task_description="Verify citations and groundedness",
                assigned_agent_type="VERIFICATION",
                dependencies=["step_2_evidence"],
                tool_name="citation_lookup",
                tool_params={"claim": goal}
            )
            nodes["step_4_report"] = PlanNode(
                node_key="step_4_report",
                task_type="REPORT_GENERATION",
                task_description="Compile findings into summary document",
                assigned_agent_type="SUPERVISOR",
                dependencies=["step_3_verify"],
                tool_name="report_generate",
                tool_params={"title": f"Research Summary: {goal}"}
            )

        # 3. Default Enterprise Intelligence Task
        else:
            nodes["step_1_explore"] = PlanNode(
                node_key="step_1_explore",
                task_type="DATA_EXPLORATION",
                task_description="Search relevant analytical datasets",
                assigned_agent_type="DATA",
                dependencies=[],
                tool_name="dataset_search",
                tool_params={"query": goal}
            )
            nodes["step_2_analyze"] = PlanNode(
                node_key="step_2_analyze",
                task_type="ANALYTICAL_QUERY",
                task_description="Evaluate metrics and run query analysis",
                assigned_agent_type="SQL",
                dependencies=["step_1_explore"],
                tool_name="metric_evaluate",
                tool_params={"metric_name": "primary_kpi"}
            )
            nodes["step_3_synthesize"] = PlanNode(
                node_key="step_3_synthesize",
                task_type="REPORT_GENERATION",
                task_description="Synthesize findings and recommendations",
                assigned_agent_type="SUPERVISOR",
                dependencies=["step_2_analyze"],
                tool_name="report_generate",
                tool_params={"title": f"Analysis Report: {goal}"}
            )

        return nodes

    def _topological_sort(self, nodes: Dict[str, PlanNode]) -> List[str]:
        """Perform topological sort to establish valid execution sequence."""
        in_degree = {k: 0 for k in nodes}
        adj = {k: [] for k in nodes}

        for k, node in nodes.items():
            for dep in node.dependencies:
                if dep in adj:
                    adj[dep].append(k)
                    in_degree[k] += 1

        queue = [k for k, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)

            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(nodes):
            raise ValueError("Cyclic dependency detected in agent plan DAG!")

        return order

    def _calculate_risk_score(self, nodes: Dict[str, PlanNode]) -> float:
        """Calculate overall risk score between 0.0 and 1.0 based on node tool risk tiers."""
        risk_weights = {
            "READ_ONLY": 0.1,
            "LOW_RISK": 0.2,
            "MEDIUM_RISK": 0.5,
            "HIGH_RISK": 0.8,
            "CRITICAL": 1.0
        }
        total_risk = 0.0
        count = 0

        for node in nodes.values():
            if node.tool_name:
                t = tool_registry.get_tool(node.tool_name)
                tier = t.risk_tier if t else "LOW_RISK"
                total_risk += risk_weights.get(tier, 0.2)
                count += 1

        return min(1.0, total_risk / max(1, count))


dag_planner = DAGPlanner()
