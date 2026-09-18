"""Agent Execution Evaluation Database Model."""

from sqlalchemy import String, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class AgentEvaluationModel(AEGISBaseModel):
    """Agent execution quality, accuracy, reasoning & cost evaluation model."""

    __tablename__ = "agent_evaluations"

    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    goal_completion_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tool_accuracy_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reasoning_quality_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rationale_evidence_alignment: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_support_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    safety_compliance_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evaluation_summary_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
