"""Decision Policy Evaluation and Risk Approval Database Models."""

from sqlalchemy import String, Text, JSON, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DecisionPolicyEvaluationModel(AEGISBaseModel):
    """Server-side policy evaluation audit model."""

    __tablename__ = "decision_policy_evaluations"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    policy_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    policy_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    policy_result: Mapped[str] = mapped_column(String(50), nullable=False)  # ALLOW, DENY, REQUIRE_APPROVAL, REQUIRE_ESCALATION, REQUIRE_REVIEW
    evaluated_conditions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    matched_rules_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=True)


class DecisionApprovalModel(AEGISBaseModel):
    """Decision-specific approval state model integrated with AEGIS governance authority."""

    __tablename__ = "decision_approvals"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    required_role: Mapped[str] = mapped_column(String(50), default="DECISION_APPROVER", nullable=False)
    approver_id: Mapped[str] = mapped_column(String(100), nullable=True)
    approval_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, APPROVED, REJECTED, EXPIRED, INVALIDATED
    approval_rationale: Mapped[str] = mapped_column(Text, nullable=True)
    approved_at: Mapped[str] = mapped_column(String(50), nullable=True)
    expires_at: Mapped[str] = mapped_column(String(50), nullable=True)
    revalidated_at: Mapped[str] = mapped_column(String(50), nullable=True)
    is_revalidated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
