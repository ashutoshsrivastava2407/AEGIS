"""Governed Action Database Model."""

from sqlalchemy import String, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class ActionModel(AEGISBaseModel):
    __tablename__ = "actions"

    decision_id: Mapped[str] = mapped_column(String(36), ForeignKey("decisions.id"), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), default="LOW", nullable=False)
    execution_state: Mapped[str] = mapped_column(String(50), default="PENDING_APPROVAL", nullable=False, index=True)
    approver: Mapped[str] = mapped_column(String(100), nullable=True)
    execution_result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
