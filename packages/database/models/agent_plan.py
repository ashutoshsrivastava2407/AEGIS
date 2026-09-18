"""Agent Plan & DAG Node Database Models."""

from sqlalchemy import String, Text, JSON, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class AgentPlanModel(AEGISBaseModel):
    """Agent execution plan DAG model."""

    __tablename__ = "agent_plans"

    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    goal_statement: Mapped[str] = mapped_column(Text, nullable=False)
    plan_status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False, index=True)  # DRAFT, APPROVED, IN_PROGRESS, COMPLETED, REJECTED, FAILED
    total_nodes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    context_snapshot_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class AgentPlanNodeModel(AEGISBaseModel):
    """Agent plan DAG node model."""

    __tablename__ = "agent_plan_nodes"

    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("agent_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    node_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    dependencies_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)  # array of parent node_keys
    assigned_agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=True)
    tool_params_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    node_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, READY, RUNNING, COMPLETED, FAILED, SKIPPED
    result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
