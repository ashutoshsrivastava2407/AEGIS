"""AEGIS Agent Contextual & Episodic Memory Store.

Provides short-term, working, episodic, and long-term memory persistence for agents.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid
import logging

logger = logging.getLogger("aegis.agents.memory")


@dataclass
class MemoryRecord:
    memory_id: str
    agent_id: Optional[str]
    run_id: Optional[str]
    memory_type: str  # SHORT_TERM, LONG_TERM, EPISODIC, WORKING
    memory_key: str
    content: Dict[str, Any]
    importance_score: float = 0.5
    tags: List[str] = field(default_factory=list)


class AgentMemoryService:
    """Memory store for agent context retention."""

    def __init__(self):
        self._memories: Dict[str, MemoryRecord] = {}

    def store_memory(
        self,
        memory_type: str,
        memory_key: str,
        content: Dict[str, Any],
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        importance_score: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> MemoryRecord:
        memory_id = str(uuid.uuid4())
        rec = MemoryRecord(
            memory_id=memory_id,
            agent_id=agent_id,
            run_id=run_id,
            memory_type=memory_type,
            memory_key=memory_key,
            content=content,
            importance_score=importance_score,
            tags=tags or []
        )
        self._memories[memory_id] = rec
        return rec

    def query_memories(
        self,
        memory_type: Optional[str] = None,
        memory_key: Optional[str] = None,
        run_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> List[MemoryRecord]:
        res = list(self._memories.values())
        if memory_type:
            res = [m for m in res if m.memory_type == memory_type]
        if memory_key:
            res = [m for m in res if m.memory_key == memory_key]
        if run_id:
            res = [m for m in res if m.run_id == run_id]
        if agent_id:
            res = [m for m in res if m.agent_id == agent_id]
        return res


agent_memory_service = AgentMemoryService()
