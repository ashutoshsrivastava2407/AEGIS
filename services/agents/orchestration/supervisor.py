"""AEGIS Multi-Agent Orchestration & Supervisor Engine.

Coordinates multi-agent execution loops, DAG traversal, loop safety checks,
verification gates, human approval triggers, and trace logging.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid
import time
import logging
from datetime import datetime, timezone

from services.agents.planning.planner import dag_planner, ExecutionPlan, PlanNode
from services.agents.orchestration.loop_guard import loop_guard
from services.agents.verification.verification_agent import verification_agent, VerificationResult
from services.agents.approvals.approval_engine import approval_engine
from services.agents.agents.specialized_agents import (
    SupervisorAgent, DataAgent, SQLAgent, ResearchRAGAgent,
    MLAgent, InvestigationAgent, ForecastingAgent, DecisionAgent, ExecutionAgent
)

logger = logging.getLogger("aegis.agents.orchestration.supervisor")


@dataclass
class AgentRunOutcome:
    run_id: str
    goal: str
    status: str  # COMPLETED, FAILED, WAITING_APPROVAL
    plan_id: str
    total_steps: int
    executed_nodes: List[Dict[str, Any]]
    verification_result: Optional[VerificationResult]
    pending_approval: Optional[Dict[str, Any]]
    output_summary: str
    duration_ms: float


class AgentSupervisorOrchestrator:
    """Master Orchestration Engine coordinating multi-agent workflows."""

    def __init__(self):
        self.agent_map = {
            "SUPERVISOR": SupervisorAgent(),
            "DATA": DataAgent(),
            "SQL": SQLAgent(),
            "RESEARCH_RAG": ResearchRAGAgent(),
            "ML": MLAgent(),
            "INVESTIGATION": InvestigationAgent(),
            "FORECASTING": ForecastingAgent(),
            "DECISION": DecisionAgent(),
            "EXECUTION": ExecutionAgent(),
            "VERIFICATION": SupervisorAgent()
        }

    def execute_run(
        self,
        goal: str,
        agent_type: str = "SUPERVISOR",
        run_id: Optional[str] = None,
        tenant_id: str = "default",
        context: Optional[Dict[str, Any]] = None
    ) -> AgentRunOutcome:
        """Execute a complete autonomous agent investigation and decision pipeline."""

        start_time = time.time()
        run_id = run_id or str(uuid.uuid4())
        context = context or {}

        logger.info(f"Starting agent run '{run_id}' for goal: '{goal}'")

        # 1. Generate DAG Execution Plan
        plan: ExecutionPlan = dag_planner.create_plan(
            goal_statement=goal,
            run_id=run_id,
            tenant_id=tenant_id,
            context=context
        )

        executed_nodes = []
        pending_approval_dict = None
        current_step = 0

        # 2. Traverse DAG in topological order
        for node_key in plan.execution_order:
            current_step += 1
            node: PlanNode = plan.nodes[node_key]

            # Loop Guard Check
            guard_check = loop_guard.evaluate_step(
                run_id=run_id,
                current_step=current_step,
                tool_name=node.tool_name or "default_tool",
                params=node.tool_params
            )
            if not guard_check.allowed:
                logger.error(f"Loop guard halted run '{run_id}': {guard_check.reason}")
                return AgentRunOutcome(
                    run_id=run_id,
                    goal=goal,
                    status="FAILED",
                    plan_id=plan.plan_id,
                    total_steps=current_step,
                    executed_nodes=executed_nodes,
                    verification_result=None,
                    pending_approval=None,
                    output_summary=f"Run failed loop guard check: {guard_check.reason}",
                    duration_ms=(time.time() - start_time) * 1000.0
                )

            # Assign specialized agent
            assigned_agent = self.agent_map.get(node.assigned_agent_type, self.agent_map["SUPERVISOR"])

            # Execute Node Task
            node_result = assigned_agent.execute_task(
                node_key=node_key,
                task_type=node.task_type,
                task_description=node.task_description,
                tool_name=node.tool_name,
                tool_params=node.tool_params,
                run_id=run_id,
                tenant_id=tenant_id
            )

            # Check if execution triggered Human Approval Gate
            exec_res = node_result.get("execution_result", {})
            if exec_res.get("requires_approval"):
                app_req = approval_engine.create_approval_request(
                    run_id=run_id,
                    tool_name=node.tool_name or "unknown",
                    risk_level=exec_res.get("risk_tier", "HIGH_RISK"),
                    requested_action=node.task_description,
                    plan_id=plan.plan_id,
                    node_key=node_key
                )
                pending_approval_dict = {
                    "approval_id": app_req.approval_id,
                    "tool_name": app_req.tool_name,
                    "risk_level": app_req.risk_level,
                    "requested_action": app_req.requested_action
                }
                node_result["status"] = "WAITING_APPROVAL"
                executed_nodes.append(node_result)

                logger.info(f"Run '{run_id}' paused at step {current_step} for human approval request '{app_req.approval_id}'")
                return AgentRunOutcome(
                    run_id=run_id,
                    goal=goal,
                    status="WAITING_APPROVAL",
                    plan_id=plan.plan_id,
                    total_steps=current_step,
                    executed_nodes=executed_nodes,
                    verification_result=None,
                    pending_approval=pending_approval_dict,
                    output_summary=f"Run paused awaiting human approval for high-risk action '{app_req.requested_action}'.",
                    duration_ms=(time.time() - start_time) * 1000.0
                )

            executed_nodes.append(node_result)

        # 3. Independent Verification Boundary
        ver_result: VerificationResult = verification_agent.verify_execution(
            claim=goal,
            evidence_references=[{"chunk_id": "chunk_001"}],
            dataset_ids=["ds_rev_01"],
            deployment_ids=["dep_forecast_01"],
            tenant_id=tenant_id
        )

        # Cleanup loop guard tracking for this run
        loop_guard.clear_run(run_id)

        duration_ms = (time.time() - start_time) * 1000.0
        summary = f"Multi-agent investigation completed successfully in {len(executed_nodes)} steps. Verification status: {'PASSED' if ver_result.is_verified else 'FAILED'}."

        return AgentRunOutcome(
            run_id=run_id,
            goal=goal,
            status="COMPLETED" if ver_result.is_verified else "FAILED",
            plan_id=plan.plan_id,
            total_steps=current_step,
            executed_nodes=executed_nodes,
            verification_result=ver_result,
            pending_approval=None,
            output_summary=summary,
            duration_ms=duration_ms
        )


supervisor_orchestrator = AgentSupervisorOrchestrator()
