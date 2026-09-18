"""AEGIS Agent Registry & Versioning Engine.

Manages agent entity definitions, versioning, state transitions (DRAFT -> VALIDATED -> ACTIVE -> SUSPENDED -> RETIRED),
and capability declarations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid
import logging
from datetime import datetime, timezone

logger = logging.getLogger("aegis.agents.registry")


@dataclass
class AgentDefinition:
    agent_id: str
    name: str
    agent_type: str
    description: str
    role_prompt: str
    risk_profile: str  # READ_ONLY, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL
    lifecycle_state: str  # DRAFT, VALIDATED, ACTIVE, SUSPENDED, RETIRED
    current_version: int = 1
    config_json: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)


class AgentRegistryService:
    """Registry managing agent catalog definitions and state machine."""

    VALID_STATE_TRANSITIONS = {
        "DRAFT": ["VALIDATED", "RETIRED"],
        "VALIDATED": ["ACTIVE", "DRAFT", "RETIRED"],
        "ACTIVE": ["SUSPENDED", "RETIRED"],
        "SUSPENDED": ["ACTIVE", "RETIRED"],
        "RETIRED": []
    }

    def __init__(self):
        self._agents: Dict[str, AgentDefinition] = {}
        self._register_default_agents()

    def register_agent(
        self,
        name: str,
        agent_type: str,
        role_prompt: str,
        description: str = "",
        risk_profile: str = "MEDIUM_RISK",
        capabilities: Optional[List[str]] = None
    ) -> AgentDefinition:
        """Register a new agent in DRAFT state."""
        agent_id = str(uuid.uuid4())
        agent = AgentDefinition(
            agent_id=agent_id,
            name=name,
            agent_type=agent_type,
            description=description,
            role_prompt=role_prompt,
            risk_profile=risk_profile,
            lifecycle_state="DRAFT",
            capabilities=capabilities or []
        )
        self._agents[agent_id] = agent
        logger.info(f"Registered agent '{name}' ({agent_type}) in DRAFT state")
        return agent

    def transition_state(self, agent_id: str, new_state: str) -> AgentDefinition:
        """Transition agent lifecycle state according to state machine rules."""
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found.")

        current = agent.lifecycle_state
        allowed = self.VALID_STATE_TRANSITIONS.get(current, [])
        if new_state not in allowed:
            raise ValueError(f"Invalid state transition from '{current}' to '{new_state}'. Allowed: {allowed}")

        agent.lifecycle_state = new_state
        logger.info(f"Agent '{agent.name}' transitioned from {current} -> {new_state}")
        return agent

    def get_agent(self, agent_id: str) -> Optional[AgentDefinition]:
        return self._agents.get(agent_id)

    def list_agents(self, lifecycle_state: Optional[str] = None, agent_type: Optional[str] = None) -> List[AgentDefinition]:
        res = list(self._agents.values())
        if lifecycle_state:
            res = [a for a in res if a.lifecycle_state == lifecycle_state]
        if agent_type:
            res = [a for a in res if a.agent_type == agent_type]
        return res

    def _register_default_agents(self) -> None:
        """Initialize standard AEGIS system agents."""
        defaults = [
            ("AEGIS Master Supervisor", "SUPERVISOR", "Master Orchestration Agent", "HIGH_RISK", ["orchestration", "reporting"]),
            ("AEGIS Data Explorer", "DATA", "Data Platform Explorer", "READ_ONLY", ["dataset_search", "schema_lookup"]),
            ("AEGIS Analytics & SQL Agent", "SQL", "Read-Only SQL Analytical Query Agent", "LOW_RISK", ["sql_query", "metric_eval"]),
            ("AEGIS Enterprise RAG Agent", "RESEARCH_RAG", "Knowledge Base Retrieval Agent", "READ_ONLY", ["hybrid_search", "citation"]),
            ("AEGIS ML Intelligence Agent", "ML", "Machine Learning Model & Drift Agent", "LOW_RISK", ["predict", "drift_check"]),
            ("AEGIS Incident Investigator", "INVESTIGATION", "Root Cause & Anomaly Investigator", "MEDIUM_RISK", ["anomaly_check", "correlation"]),
            ("AEGIS Demand Forecaster", "FORECASTING", "Time Series Forecasting Agent", "READ_ONLY", ["forecasting", "trend_proj"]),
            ("AEGIS Decision Engine Agent", "DECISION", "Strategic Decision & Tradeoff Agent", "MEDIUM_RISK", ["tradeoff_eval", "option_score"]),
            ("AEGIS Action Execution Agent", "EXECUTION", "Governed Action & Workflow Execution Agent", "HIGH_RISK", ["notification", "workflow_trigger"]),
            ("AEGIS Independent Verifier", "VERIFICATION", "Verification & Groundedness Agent", "READ_ONLY", ["verification", "audit"])
        ]
        for name, a_type, desc, risk, caps in defaults:
            a = AgentDefinition(
                agent_id=f"agent_{a_type.lower()}_01",
                name=name,
                agent_type=a_type,
                description=desc,
                role_prompt=f"Role prompt for {name}",
                risk_profile=risk,
                lifecycle_state="ACTIVE",
                capabilities=caps
            )
            self._agents[a.agent_id] = a


agent_registry = AgentRegistryService()
