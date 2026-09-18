"""Agent Tool & Permission Database Models."""

from sqlalchemy import String, Text, JSON, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class AgentToolModel(AEGISBaseModel):
    """Tool definition catalog model."""

    __tablename__ = "agent_tools"

    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # DATA_PLATFORM, ANALYTICS, ML_PLATFORM, KNOWLEDGE_RAG, STREAMING, WORKFLOW, NOTIFICATION
    description: Mapped[str] = mapped_column(Text, nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(50), default="LOW_RISK", nullable=False)  # READ_ONLY, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL
    schema_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_governed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rate_limit_per_min: Mapped[int] = mapped_column(Integer, default=60, nullable=False)


class AgentToolPermissionModel(AEGISBaseModel):
    """Agent tool permission mapping model."""

    __tablename__ = "agent_tool_permissions"

    tool_id: Mapped[str] = mapped_column(String(36), ForeignKey("agent_tools.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    permission_level: Mapped[str] = mapped_column(String(50), default="EXECUTE", nullable=False)  # READ, EXECUTE, ADMIN
    conditions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
