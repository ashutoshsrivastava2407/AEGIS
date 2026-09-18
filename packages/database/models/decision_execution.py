"""Decision Action Execution, Outcome, Feedback Calibration, Trace, and Outbox Database Models."""

from sqlalchemy import String, Text, JSON, Float, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DecisionActionModel(AEGISBaseModel):
    """Decision domain Action model referencing versioned ActionContract."""

    __tablename__ = "decision_actions"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    option_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    contract_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_resource: Mapped[str] = mapped_column(String(255), nullable=False)
    parameters_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    risk_classification: Mapped[str] = mapped_column(String(50), default="MEDIUM_RISK", nullable=False)
    side_effects_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    reversibility: Mapped[str] = mapped_column(String(50), default="REVERSIBLE", nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    preconditions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    postconditions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    compensation_method: Mapped[str] = mapped_column(String(100), nullable=True)
    execution_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, EXECUTING, EXECUTED, FAILED, REVERTED
    execution_result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    postconditions_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class DecisionOutcomeModel(AEGISBaseModel):
    """Outcome tracking model with attribution classification."""

    __tablename__ = "decision_outcomes"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    attribution_classification: Mapped[str] = mapped_column(String(50), default="OBSERVED", nullable=False)  # EXPECTED, OBSERVED, MODELED, CAUSALLY_ESTIMATED
    expected_impact_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_impact_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    variance_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    observed_kpis_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    attribution_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    measurement_window_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)


class DecisionFeedbackModel(AEGISBaseModel):
    """Controlled Calibration Proposal model for versioned governance updates."""

    __tablename__ = "decision_feedbacks"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    outcome_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    proposal_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    target_component: Mapped[str] = mapped_column(String(100), nullable=False)  # CRITERIA_WEIGHT, RISK_THRESHOLD, POLICY_RULE
    previous_config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    proposed_config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    offline_evaluation_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    shadow_evaluation_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    governance_status: Mapped[str] = mapped_column(String(50), default="PROPOSED", nullable=False, index=True)  # PROPOSED, EVALUATED, APPROVED, ROLLED_OUT, ROLLED_BACK
    approved_by: Mapped[str] = mapped_column(String(100), nullable=True)
    is_rolled_out: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rollback_target_version: Mapped[str] = mapped_column(String(20), nullable=True)


class DecisionTraceEventModel(AEGISBaseModel):
    """Observable trace event log model."""

    __tablename__ = "decision_trace_events"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    stage_number: Mapped[int] = mapped_column(Integer, nullable=False)
    stage_name: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class DecisionOutboxModel(AEGISBaseModel):
    """Transactional Outbox Pattern model for atomic event dispatching."""

    __tablename__ = "decision_outbox_events"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    dispatch_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, DISPATCHED, FAILED
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
