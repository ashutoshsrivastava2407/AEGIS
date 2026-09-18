"""Human-in-the-Loop Approval Database Model."""

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel
from datetime import datetime


class AgentApprovalModel(AEGISBaseModel):
    """Human approval gate model for high risk actions."""

    __tablename__ = "agent_approvals"

    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    node_key: Mapped[str] = mapped_column(String(100), nullable=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # MEDIUM_RISK, HIGH_RISK, CRITICAL
    requested_action: Mapped[str] = mapped_column(Text, nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=True)
    approval_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, APPROVED, REJECTED, EXPIRED, BYPASSED
    approved_by: Mapped[str] = mapped_column(String(100), nullable=True)
    comments: Mapped[str] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
