"""AEGIS Specialized Agent Base Class.

Defines standard execution interface, step logging, thought process logging, and tool invocation hooks.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import time
import logging
import uuid

from services.agents.tools.executor import tool_executor

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
        run_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Invoke governed tool executor on behalf of this agent."""
        return tool_executor.execute_tool(
            tool_name=tool_name,
            params=params,
            agent_type=self.agent_type,
            run_id=run_id,
            tenant_id=tenant_id
        )
