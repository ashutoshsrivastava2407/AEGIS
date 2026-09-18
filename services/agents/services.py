"""AEGIS Autonomous Agent Platform Unified Service Facade.

Unified application service orchestrating agents, versioning, governed tool platform,
authorization engine, DAG planning, multi-agent supervisor, human approval gates,
verification boundaries, memory store, and quantitative evaluation.
"""

from typing import Any, Dict, List, Optional
import logging

from services.agents.orchestration.supervisor import supervisor_orchestrator, AgentRunOutcome
from services.agents.registry.agent_registry import agent_registry, AgentDefinition
from services.agents.tools.tool_registry import tool_registry, ToolDefinition
from services.agents.tools.authorization import authorization_engine
from services.agents.approvals.approval_engine import approval_engine, ApprovalRequest
from services.agents.verification.verification_agent import verification_agent, VerificationResult
from services.agents.memory.agent_memory import agent_memory_service
from services.agents.evaluation.evaluator import agent_evaluator, AgentEvaluationMetrics

logger = logging.getLogger("aegis.agents.service")


class AgentPlatformService:
    """Unified Facade for AEGIS Autonomous Agent Platform operations."""

    def execute_agent_run(
        self,
        goal: str,
        agent_type: str = "SUPERVISOR",
        tenant_id: str = "default",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a complete autonomous agent goal or investigation workflow."""
        outcome: AgentRunOutcome = supervisor_orchestrator.execute_run(
            goal=goal,
            agent_type=agent_type,
            tenant_id=tenant_id,
            context=context
        )

        ver_dict = None
        if outcome.verification_result:
            ver_dict = {
                "is_verified": outcome.verification_result.is_verified,
                "groundedness_score": outcome.verification_result.groundedness_score,
                "data_quality_passed": outcome.verification_result.data_quality_passed,
                "model_drift_passed": outcome.verification_result.model_drift_passed,
                "summary": outcome.verification_result.verification_summary,
                "issues": outcome.verification_result.issues_detected
            }

        # Quantitative Evaluation
        eval_metrics: AgentEvaluationMetrics = agent_evaluator.evaluate_run(
            run_id=outcome.run_id,
            agent_type=agent_type,
            executed_steps=outcome.total_steps,
            is_successful=(outcome.status == "COMPLETED"),
            groundedness_score=outcome.verification_result.groundedness_score if outcome.verification_result else 0.9,
            duration_ms=outcome.duration_ms
        )

        return {
            "run_id": outcome.run_id,
            "goal": outcome.goal,
            "status": outcome.status,
            "plan_id": outcome.plan_id,
            "total_steps": outcome.total_steps,
            "executed_nodes": outcome.executed_nodes,
            "verification": ver_dict,
            "pending_approval": outcome.pending_approval,
            "output_summary": outcome.output_summary,
            "duration_ms": outcome.duration_ms,
            "evaluation": {
                "goal_completion_score": eval_metrics.goal_completion_score,
                "tool_accuracy_score": eval_metrics.tool_accuracy_score,
                "reasoning_quality_score": eval_metrics.reasoning_quality_score,
                "safety_compliance_score": eval_metrics.safety_compliance_score,
                "total_cost_usd": eval_metrics.total_cost_usd,
                "total_latency_ms": eval_metrics.total_latency_ms
            }
        }

    # Agent Catalog & Lifecycle
    def list_agents(self, lifecycle_state: Optional[str] = None, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        agents = agent_registry.list_agents(lifecycle_state, agent_type)
        return [
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "agent_type": a.agent_type,
                "description": a.description,
                "risk_profile": a.risk_profile,
                "lifecycle_state": a.lifecycle_state,
                "current_version": a.current_version,
                "capabilities": a.capabilities
            }
            for a in agents
        ]

    def create_agent(self, name: str, agent_type: str, role_prompt: str, description: str = "", risk_profile: str = "MEDIUM_RISK") -> Dict[str, Any]:
        agent = agent_registry.register_agent(name, agent_type, role_prompt, description, risk_profile)
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "agent_type": agent.agent_type,
            "lifecycle_state": agent.lifecycle_state
        }

    def transition_agent_state(self, agent_id: str, new_state: str) -> Dict[str, Any]:
        agent = agent_registry.transition_state(agent_id, new_state)
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "lifecycle_state": agent.lifecycle_state
        }

    # Tool Catalog & Permissions
    def list_tools(self, category: Optional[str] = None, risk_tier: Optional[str] = None) -> List[Dict[str, Any]]:
        tools = tool_registry.list_tools(category, risk_tier)
        return [
            {
                "tool_name": t.tool_name,
                "category": t.category,
                "description": t.description,
                "risk_tier": t.risk_tier,
                "is_governed": t.is_governed,
                "rate_limit_per_min": t.rate_limit_per_min,
                "schema_json": t.schema_json
            }
            for t in tools
        ]

    # Human Approval Gates
    def list_pending_approvals(self, run_id: Optional[str] = None) -> List[Dict[str, Any]]:
        approvals = approval_engine.list_pending_approvals(run_id)
        return [
            {
                "approval_id": a.approval_id,
                "run_id": a.run_id,
                "tool_name": a.tool_name,
                "risk_level": a.risk_level,
                "requested_action": a.requested_action,
                "justification": a.justification,
                "approval_status": a.approval_status,
                "created_at": a.created_at,
                "expires_at": a.expires_at
            }
            for a in approvals
        ]

    def approve_action(self, approval_id: str, approved_by: str = "admin", comments: str = "Approved") -> Dict[str, Any]:
        app = approval_engine.approve_request(approval_id, approved_by, comments)
        return {
            "approval_id": app.approval_id,
            "approval_status": app.approval_status,
            "approved_by": app.approved_by,
            "comments": app.comments
        }

    def reject_action(self, approval_id: str, rejected_by: str = "admin", comments: str = "Rejected") -> Dict[str, Any]:
        app = approval_engine.reject_request(approval_id, rejected_by, comments)
        return {
            "approval_id": app.approval_id,
            "approval_status": app.approval_status,
            "approved_by": app.approved_by,
            "comments": app.comments
        }


agent_platform_service = AgentPlatformService()
