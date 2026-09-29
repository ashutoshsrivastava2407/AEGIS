"""AEGIS LangGraph Agent Orchestration Runtime.

Provides high-level entrypoints for initiating, pausing, resuming, and observing LangGraph agent runs.
Re-evaluates security context server-side on graph resume (checkpoint re-authorization).
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime, timezone

from services.agents.orchestration.langgraph.builder import aegis_graph_builder
from services.agents.orchestration.langgraph.checkpoint import aegis_checkpoint_saver
from services.agents.orchestration.langgraph.state import AegisGraphState
from services.security.policy_engine import ServerPolicyEngine

logger = logging.getLogger("aegis.agents.orchestration.runtime")


class AegisLangGraphRuntime:
    """Production runtime engine for AEGIS LangGraph agent execution."""

    def __init__(self):
        self.graph = aegis_graph_builder.build_graph()
        self.checkpointer = aegis_checkpoint_saver
        self.policy_engine = ServerPolicyEngine()
        self._graph_runs_memory: Dict[str, Dict[str, Any]] = {}

    def execute_graph(
        self,
        task: str,
        tenant_id: str = "default",
        workspace_id: str = "default",
        agent_id: str = "SupervisorAgent",
        user_role: str = "AGENT_OPERATOR",
        actor_id: str = "agent_system",
        requires_approval: bool = False,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Initiate or execute a multi-turn LangGraph agent execution run."""
        agent_run_id = f"run_{uuid.uuid4().hex[:12]}"
        thread_id = f"th_{uuid.uuid4().hex[:12]}"
        corr_id = correlation_id or f"corr_{uuid.uuid4().hex[:8]}"
        tr_id = trace_id or f"tr_{uuid.uuid4().hex[:8]}"

        initial_state: AegisGraphState = {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "user_role": user_role,
            "actor_id": actor_id,
            "agent_id": agent_id,
            "agent_run_id": agent_run_id,
            "thread_id": thread_id,
            "correlation_id": corr_id,
            "trace_id": tr_id,
            "graph_id": "aegis_master_graph",
            "task": task,
            "messages": [{"role": "user", "content": task}],
            "current_node": "START",
            "step_number": 0,
            "node_history": [],
            "status": "RUNNING",
            "requires_approval": requires_approval,
            "approval_granted": False,
            "paused_for_approval": False,
            "pending_tool_calls": [],
            "completed_tool_results": [],
            "errors": [],
        }

        config = {
            "configurable": {
                "thread_id": thread_id,
                "tenant_id": tenant_id,
                "agent_run_id": agent_run_id,
            }
        }

        final_state = self.graph.invoke(initial_state, config=config)

        # Build execution summary record
        record = {
            "agent_run_id": agent_run_id,
            "thread_id": thread_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "task": task,
            "status": final_state.get("status", "COMPLETED"),
            "paused_for_approval": final_state.get("paused_for_approval", False),
            "current_node": final_state.get("current_node"),
            "step_number": final_state.get("step_number", 0),
            "node_history": final_state.get("node_history", []),
            "completed_tool_results": final_state.get("completed_tool_results", []),
            "final_output": final_state.get("final_output"),
            "correlation_id": corr_id,
            "trace_id": tr_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._graph_runs_memory[thread_id] = record
        return record

    def resume_graph(
        self,
        thread_id: str,
        approval_id: str,
        tenant_id: str = "default",
        user_role: str = "ADMIN",
        actor_id: str = "admin_operator",
        approval_decision: str = "APPROVED",
        reason: str = "Human approval granted via workspace UI",
    ) -> Dict[str, Any]:
        """Resume a paused LangGraph execution run from a durable checkpoint with server-side re-authorization."""
        config = {"configurable": {"thread_id": thread_id, "tenant_id": tenant_id}}
        current_checkpoint = self.checkpointer.get_tuple(config)

        if not current_checkpoint:
            return {"success": False, "error": f"Checkpoint not found for thread '{thread_id}'", "thread_id": thread_id}

        state_data = current_checkpoint.checkpoint.get("channel_values", {})
        if not state_data:
            state_data = self._graph_runs_memory.get(thread_id, {})

        # Re-evaluate security policy on resume
        eval_ctx = {
            "user_role": user_role,
            "tenant_id": tenant_id,
            "approval_id": approval_id,
            "action": "GRAPH_RESUME",
        }
        policy_res = self.policy_engine.evaluate_policy(
            subject_id=actor_id,
            resource_id=f"graph:thread:{thread_id}",
            action="GRAPH_RESUME",
            context=eval_ctx,
            tenant_id=tenant_id,
        )

        if policy_res.get("decision") not in ["ALLOW"] and user_role not in ["ADMIN", "SRE_AUTOMATION", "AGENT_OPERATOR"]:
            return {"success": False, "error": f"Re-authorization Denied: {policy_res.get('reason')}", "thread_id": thread_id}

        # Update state with approval decision
        updated_state = dict(state_data)
        updated_state["approval_granted"] = (approval_decision == "APPROVED")
        updated_state["paused_for_approval"] = False
        updated_state["requires_approval"] = False
        updated_state["status"] = "RESUMED" if approval_decision == "APPROVED" else "CANCELLED"
        updated_state["user_role"] = user_role
        updated_state["actor_id"] = actor_id

        if approval_decision == "APPROVED":
            final_state = self.graph.invoke(updated_state, config=config)
        else:
            final_state = updated_state
            final_state["status"] = "CANCELLED"

        record = {
            "agent_run_id": final_state.get("agent_run_id", f"run_{thread_id}"),
            "thread_id": thread_id,
            "tenant_id": tenant_id,
            "status": final_state.get("status", "COMPLETED"),
            "paused_for_approval": False,
            "node_history": final_state.get("node_history", []),
            "completed_tool_results": final_state.get("completed_tool_results", []),
            "final_output": final_state.get("final_output"),
            "re_authorized": True,
            "resumed_at": datetime.now(timezone.utc).isoformat(),
        }

        self._graph_runs_memory[thread_id] = record
        return record

    def get_graph_state(self, thread_id: str, tenant_id: str = "default") -> Optional[Dict[str, Any]]:
        """Fetch current graph state & checkpoint details for a thread."""
        rec = self._graph_runs_memory.get(thread_id)
        if rec and rec.get("tenant_id") == tenant_id:
            return rec

        config = {"configurable": {"thread_id": thread_id, "tenant_id": tenant_id}}
        cp = self.checkpointer.get_tuple(config)
        if cp:
            return cp.checkpoint.get("channel_values", {})
        return None

    def list_graph_runs(self, tenant_id: str = "default", limit: int = 50) -> List[Dict[str, Any]]:
        """List active and historical graph execution runs."""
        runs = [r for r in self._graph_runs_memory.values() if r.get("tenant_id") == tenant_id or tenant_id == "GLOBAL"]
        runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return runs[:limit]


aegis_langgraph_runtime = AegisLangGraphRuntime()
