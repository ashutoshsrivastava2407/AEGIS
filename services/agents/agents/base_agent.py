"""AEGIS Specialized Agent Base Class.

Defines standard execution interface, step logging, thought process logging,
and multi-turn governed tool execution loop with loop guards.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import time
import logging
import uuid
import hashlib
import json

from services.agents.tools.executor import tool_executor
from services.agents.tools.tool_registry import tool_registry
from services.llm.services import llm_gateway_service

logger = logging.getLogger("aegis.agents.base")


class BaseAgent(ABC):
    """Abstract base class for all specialized AEGIS agents."""

    def __init__(self, agent_type: str, role_prompt: str, risk_profile: str = "MEDIUM_RISK"):
        self.agent_type = agent_type
        self.role_prompt = role_prompt
        self.risk_profile = risk_profile

    @abstractmethod
    def execute_task(
        self,
        node_key: str,
        task_type: str,
        task_description: str,
        tool_name: Optional[str] = None,
        tool_params: Optional[Dict[str, Any]] = None,
        run_id: str = "default_run",
        tenant_id: str = "default"
    ) -> Dict[str, Any]:
        """Execute assigned task node and return output result payload."""
        pass

    def execute_governed_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        run_id: str = "default_run",
        tenant_id: str = "default",
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        approval_granted: bool = False
    ) -> Dict[str, Any]:
        """Invoke governed tool executor on behalf of this agent."""
        return tool_executor.execute_tool(
            tool_name=tool_name,
            params=params,
            agent_type=self.agent_type,
            run_id=run_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            approval_granted=approval_granted
        )

    def execute_multi_turn_tool_loop(
        self,
        query: str,
        max_turns: int = 10,
        run_id: Optional[str] = None,
        tenant_id: str = "default",
        auto_approve_high_risk: bool = False
    ) -> Dict[str, Any]:
        """Execute multi-turn agentic tool selection loop driven dynamically by LLM tool calls & results."""

        start_time = time.time()
        run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"
        trace_id = f"tr_{uuid.uuid4().hex[:8]}"
        correlation_id = f"corr_{uuid.uuid4().hex[:8]}"

        tools_schema = tool_registry.export_tools_schema(provider_format="openai")
        executed_tool_calls: List[Dict[str, Any]] = []
        conversation_context: List[str] = [f"User Query: {query}"]
        seen_call_hashes: Dict[str, int] = {}
        loop_guard_triggered = False

        for turn in range(1, max_turns + 1):
            prompt = "\n".join(conversation_context)

            # LLM Gateway call requesting tool selection or text synthesis
            llm_res = llm_gateway_service.generate(
                prompt=prompt,
                system_prompt=self.role_prompt,
                tools=tools_schema,
                tenant_id=tenant_id
            )

            tool_calls = llm_res.get("tool_calls", [])

            if not tool_calls:
                # LLM synthesized final text answer without requesting additional tools
                final_answer = llm_res.get("content", "Task completed.")
                duration_ms = (time.time() - start_time) * 1000.0
                return {
                    "status": "COMPLETED",
                    "run_id": run_id,
                    "agent_type": self.agent_type,
                    "turns_count": turn,
                    "executed_tool_calls": executed_tool_calls,
                    "final_answer": final_answer,
                    "duration_ms": duration_ms,
                    "trace_id": trace_id,
                    "loop_guard_triggered": loop_guard_triggered
                }

            # Process LLM requested tool call
            for tc in tool_calls:
                tool_name = tc.get("tool_name", "")
                arguments = tc.get("arguments", {})

                # Duplicate call argument hash detection (Loop Guard)
                arg_hash = hashlib.sha256(json.dumps({"t": tool_name, "a": arguments}, sort_keys=True).encode()).hexdigest()
                seen_call_hashes[arg_hash] = seen_call_hashes.get(arg_hash, 0) + 1

                if seen_call_hashes[arg_hash] > 2:
                    logger.warning(f"Loop guard triggered for agent '{self.agent_type}': Repeated identical call '{tool_name}'")
                    loop_guard_triggered = True
                    break

                # Execute tool call through GovernedToolExecutor
                tool_res = self.execute_governed_tool(
                    tool_name=tool_name,
                    params=arguments,
                    run_id=run_id,
                    tenant_id=tenant_id,
                    correlation_id=correlation_id,
                    trace_id=trace_id,
                    approval_granted=auto_approve_high_risk
                )

                tool_record = {
                    "turn": turn,
                    "call_id": tool_res.get("call_id", f"call_{uuid.uuid4().hex[:8]}"),
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "status": tool_res.get("status", "EXECUTED"),
                    "risk_tier": tool_res.get("risk_tier", "LOW_RISK"),
                    "duration_ms": tool_res.get("duration_ms", 0.0),
                    "result": tool_res.get("data", tool_res.get("error")),
                    "is_authorized": tool_res.get("is_authorized", True),
                    "result_schema_valid": tool_res.get("result_schema_valid", True),
                    "trace_id": trace_id
                }
                executed_tool_calls.append(tool_record)

                # Feed tool result back into agent context for next turn
                res_str = json.dumps(tool_res.get("data", tool_res.get("error", {})), default=str)
                conversation_context.append(f"Turn {turn} Tool '{tool_name}' Result: {res_str}")

            if loop_guard_triggered:
                break

        duration_ms = (time.time() - start_time) * 1000.0
        return {
            "status": "COMPLETED" if not loop_guard_triggered else "LOOP_GUARD_STOPPED",
            "run_id": run_id,
            "agent_type": self.agent_type,
            "turns_count": len(executed_tool_calls),
            "executed_tool_calls": executed_tool_calls,
            "final_answer": f"Agent multi-turn tool execution finished after {len(executed_tool_calls)} tool calls.",
            "duration_ms": duration_ms,
            "trace_id": trace_id,
            "loop_guard_triggered": loop_guard_triggered
        }
