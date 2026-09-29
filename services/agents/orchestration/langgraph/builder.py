"""AEGIS LangGraph Graph Builder.

Assembles StateGraph(AegisGraphState) with conditional routing, checkpoint saver, and node transitions.
"""

import logging
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, START, END

from services.agents.orchestration.langgraph.state import AegisGraphState
from services.agents.orchestration.langgraph.checkpoint import aegis_checkpoint_saver
from services.agents.orchestration.langgraph.nodes import (
    memory_retrieval_node,
    task_classification_node,
    supervisor_node,
    specialized_agent_node,
    tool_selection_node,
    tool_execution_node,
    result_validation_node,
    memory_write_node,
    decision_node,
    approval_node,
    workflow_node,
    verification_node,
    final_response_node,
)

logger = logging.getLogger("aegis.agents.orchestration.builder")


class AegisLangGraphBuilder:
    """Builder for constructing the master AEGIS LangGraph execution graph."""

    def __init__(self, checkpointer=None):
        self.checkpointer = checkpointer or aegis_checkpoint_saver

    def build_graph(self):
        """Construct and compile the AEGIS StateGraph."""
        builder = StateGraph(AegisGraphState)

        # Register nodes
        builder.add_node("MEMORY_RETRIEVAL", memory_retrieval_node)
        builder.add_node("TASK_CLASSIFICATION", task_classification_node)
        builder.add_node("SUPERVISOR", supervisor_node)
        builder.add_node("SPECIALIZED_AGENT", specialized_agent_node)
        builder.add_node("TOOL_SELECTION", tool_selection_node)
        builder.add_node("TOOL_EXECUTION", tool_execution_node)
        builder.add_node("RESULT_VALIDATION", result_validation_node)
        builder.add_node("MEMORY_WRITE", memory_write_node)
        builder.add_node("DECISION", decision_node)
        builder.add_node("APPROVAL", approval_node)
        builder.add_node("WORKFLOW", workflow_node)
        builder.add_node("VERIFICATION", verification_node)
        builder.add_node("FINAL_RESPONSE", final_response_node)

        # Edge definitions
        builder.add_edge(START, "MEMORY_RETRIEVAL")
        builder.add_edge("MEMORY_RETRIEVAL", "TASK_CLASSIFICATION")
        builder.add_edge("TASK_CLASSIFICATION", "SUPERVISOR")
        builder.add_edge("SUPERVISOR", "SPECIALIZED_AGENT")
        builder.add_edge("SPECIALIZED_AGENT", "TOOL_SELECTION")
        builder.add_edge("TOOL_SELECTION", "TOOL_EXECUTION")

        # Conditional edge from TOOL_EXECUTION: check if approval paused
        builder.add_conditional_edges(
            "TOOL_EXECUTION",
            self._route_after_tool_execution,
            {
                "RESULT_VALIDATION": "RESULT_VALIDATION",
                "APPROVAL": "APPROVAL",
                "END": END,
            }
        )

        builder.add_edge("RESULT_VALIDATION", "MEMORY_WRITE")
        builder.add_edge("MEMORY_WRITE", "DECISION")
        builder.add_edge("DECISION", "APPROVAL")

        # Conditional edge from APPROVAL: check if paused for human approval
        builder.add_conditional_edges(
            "APPROVAL",
            self._route_after_approval,
            {
                "WORKFLOW": "WORKFLOW",
                "END": END,
            }
        )

        builder.add_edge("WORKFLOW", "VERIFICATION")
        builder.add_edge("VERIFICATION", "FINAL_RESPONSE")
        builder.add_edge("FINAL_RESPONSE", END)

        return builder.compile(checkpointer=self.checkpointer)

    def _route_after_tool_execution(self, state: AegisGraphState) -> str:
        """Route conditionally after tool execution based on approval requirement."""
        if state.get("paused_for_approval"):
            return "APPROVAL"
        return "RESULT_VALIDATION"

    def _route_after_approval(self, state: AegisGraphState) -> str:
        """Route conditionally after approval check."""
        if state.get("paused_for_approval"):
            return "END"
        return "WORKFLOW"


aegis_graph_builder = AegisLangGraphBuilder()
