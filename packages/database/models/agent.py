"""Agent, Version, Capability & Execution Run Database Models."""

from sqlalchemy import String, Text, JSON, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class AgentModel(AEGISBaseModel):
    """Agent entity model."""

    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # SUPERVISOR, DATA, SQL, RESEARCH_RAG, ML, INVESTIGATION, FORECASTING, DECISION, EXECUTION, VERIFICATION
    description: Mapped[str] = mapped_column(Text, nullable=True)
    role_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    risk_profile: Mapped[str] = mapped_column(String(50), default="MEDIUM_RISK", nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False, index=True)  # DRAFT, VALIDATED, ACTIVE, SUSPENDED, RETIRED
    current_version_id: Mapped[str] = mapped_column(String(36), nullable=True)
    config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class AgentVersionModel(AEGISBaseModel):
    """Agent version tracking model."""

    __tablename__ = "agent_versions"

    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    role_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    system_instructions: Mapped[str] = mapped_column(Text, nullable=True)
    tools_configured: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    changelog: Mapped[str] = mapped_column(Text, nullable=True)


class AgentCapabilityModel(AEGISBaseModel):
    """Agent capability definition model."""

    __tablename__ = "agent_capabilities"

    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    capability_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    capability_category: Mapped[str] = mapped_column(String(50), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    constraints_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class AgentRunModel(AEGISBaseModel):
    """Agent execution run database model."""

    __tablename__ = "agent_runs"

    agent_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # SUPERVISOR, DATA, RAG, DECISION, etc.
    execution_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # PENDING, RUNNING, COMPLETED, FAILED
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tool_calls: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    evidence_references: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    output_summary: Mapped[str] = mapped_column(Text, nullable=True)
    error_details: Mapped[str] = mapped_column(Text, nullable=True)
    agent_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    plan_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    risk_tier: Mapped[str] = mapped_column(String(50), default="LOW_RISK", nullable=False)

