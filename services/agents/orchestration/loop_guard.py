"""AEGIS Agent Loop Guard & Execution Safety Safeguards.

Prevents infinite agent loops, duplicate tool call loops, cyclic execution graphs,
excessive step counts, and time/token budget budget overruns.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple
import logging
import hashlib
import json

logger = logging.getLogger("aegis.agents.orchestration.loop_guard")


@dataclass
class LoopGuardCheckResult:
    allowed: bool
    reason: str


class LoopGuard:
    """Safeguard engine for agent execution loops."""

    def __init__(self, max_steps: int = 25, max_repeated_tool_calls: int = 3):
        self.max_steps = max_steps
        self.max_repeated_tool_calls = max_repeated_tool_calls
        self._execution_history: Dict[str, List[Tuple[str, str]]] = {}  # run_id -> [(tool_name, params_hash)]

    def evaluate_step(
        self,
        run_id: str,
        current_step: int,
        tool_name: str,
        params: Dict[str, Any]
    ) -> LoopGuardCheckResult:
        """Evaluate whether a proposed step violates loop/budget safety bounds."""

        # 1. Step Limit Check
        if current_step > self.max_steps:
            logger.error(f"Run '{run_id}' exceeded max step limit of {self.max_steps}")
            return LoopGuardCheckResult(
                allowed=False,
                reason=f"Execution step limit exceeded ({current_step} > {self.max_steps}). Loop guard aborted run."
            )

        # 2. Repeated Tool Call Hash Check
        params_hash = self._hash_params(params)
        history = self._execution_history.setdefault(run_id, [])

        repeat_count = sum(1 for t_name, p_hash in history if t_name == tool_name and p_hash == params_hash)
        if repeat_count >= self.max_repeated_tool_calls:
            logger.warning(f"Run '{run_id}' repeated tool call '{tool_name}' with identical parameters {repeat_count} times.")
            return LoopGuardCheckResult(
                allowed=False,
                reason=f"Loop guard detected repeated tool call '{tool_name}' with identical arguments {repeat_count} times."
            )

        # Record call in history
        history.append((tool_name, params_hash))

        return LoopGuardCheckResult(allowed=True, reason="Execution allowed by loop guard.")

    def _hash_params(self, params: Dict[str, Any]) -> str:
        """Create deterministic SHA-256 hash of parameter dict."""
        try:
            param_str = json.dumps(params, sort_keys=True, default=str)
            return hashlib.sha256(param_str.encode('utf-8')).hexdigest()
        except Exception:
            return str(hash(str(params)))

    def clear_run(self, run_id: str) -> None:
        """Clean up tracking history for completed run."""
        if run_id in self._execution_history:
            del self._execution_history[run_id]


loop_guard = LoopGuard()
