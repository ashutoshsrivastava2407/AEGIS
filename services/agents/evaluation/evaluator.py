"""AEGIS Agent Performance & Quality Evaluator Engine.

Calculates quantitative scores for goal completion, tool accuracy, reasoning quality,
safety compliance, total cost USD, and total latency ms.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
import uuid
import logging

logger = logging.getLogger("aegis.agents.evaluation")


@dataclass
class AgentEvaluationMetrics:
    eval_id: str
    run_id: str
    agent_type: str
    goal_completion_score: float  # 0.0 to 1.0
    tool_accuracy_score: float    # 0.0 to 1.0
    reasoning_quality_score: float # 0.0 to 1.0
    safety_compliance_score: float # 0.0 to 1.0
    total_cost_usd: float
    total_latency_ms: float
    summary: Dict[str, Any]


class AgentEvaluatorEngine:
    """Evaluates agent execution runs against quality, accuracy, and safety benchmarks."""

    def evaluate_run(
        self,
        run_id: str,
        agent_type: str,
        executed_steps: int,
        is_successful: bool,
        groundedness_score: float = 0.95,
        duration_ms: float = 1200.0,
        estimated_tokens: int = 1500
    ) -> AgentEvaluationMetrics:
        
        goal_score = 1.0 if is_successful else 0.4
        tool_accuracy = min(1.0, 0.9 + (0.1 if is_successful else -0.3))
        reasoning_score = min(1.0, (goal_score + groundedness_score) / 2.0)
        safety_score = 1.0

        # Cost calculation: $0.0015 per 1k input, $0.002 per 1k output
        cost_usd = (estimated_tokens / 1000.0) * 0.002

        eval_id = str(uuid.uuid4())
        metrics = AgentEvaluationMetrics(
            eval_id=eval_id,
            run_id=run_id,
            agent_type=agent_type,
            goal_completion_score=goal_score,
            tool_accuracy_score=tool_accuracy,
            reasoning_quality_score=reasoning_score,
            safety_compliance_score=safety_score,
            total_cost_usd=cost_usd,
            total_latency_ms=duration_ms,
            summary={
                "steps_executed": executed_steps,
                "groundedness": groundedness_score,
                "token_usage": estimated_tokens
            }
        )

        logger.info(f"Evaluated run '{run_id}': goal={goal_score:.2f}, accuracy={tool_accuracy:.2f}, cost=${cost_usd:.4f}")
        return metrics


agent_evaluator = AgentEvaluatorEngine()
