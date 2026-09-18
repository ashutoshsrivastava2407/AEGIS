"""Enterprise Command Center, Continuous Learning, and Outcome Attribution Models."""

from sqlalchemy import String, Text, JSON, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class CommandCenterSnapshotModel(AEGISBaseModel):
    """Command Center Executive Snapshot Model."""

    __tablename__ = "command_center_snapshots"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    snapshot_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    health_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    health_breakdown_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    active_incidents_count: Mapped[int] = mapped_column(default=0, nullable=False)
    pending_approvals_count: Mapped[int] = mapped_column(default=0, nullable=False)
    active_learning_signals_count: Mapped[int] = mapped_column(default=0, nullable=False)
    snapshot_timestamp: Mapped[str] = mapped_column(String(50), nullable=False)


class LearningSignalModel(AEGISBaseModel):
    """Continuous Learning Operational Signal Tracking Model."""

    __tablename__ = "learning_signals"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    signal_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    dimension: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # DATA, ML, RAG, AGENT, DECISION, WORKFLOW, OPERATIONS
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_component: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    detected_at: Mapped[str] = mapped_column(String(50), nullable=False)


class ImprovementCandidateModel(AEGISBaseModel):
    """Governed Continuous Learning Improvement Candidate Lifecycle Model."""

    __tablename__ = "improvement_candidates"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    target_subsystem: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # DATA, ML, RAG, AGENT, DECISION, WORKFLOW, OPERATIONS
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OBSERVED", nullable=False, index=True)
    # Lifecycle: OBSERVED -> CANDIDATE -> EVALUATING -> VALIDATED -> APPROVED -> SHADOW -> PROMOTED -> MONITORED -> ROLLED_BACK
    proposal_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    evaluation_result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    policy_evaluation_id: Mapped[str] = mapped_column(String(100), nullable=True)
    approval_id: Mapped[str] = mapped_column(String(100), nullable=True)
    promoted_at: Mapped[str] = mapped_column(String(50), nullable=True)


class OutcomeObservationModel(AEGISBaseModel):
    """Outcome Attribution & Difference-in-Differences Observation Model."""

    __tablename__ = "outcome_observations"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    observation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    action_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    decision_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    methodology: Mapped[str] = mapped_column(String(100), default="AEGIS_DiD_v1.0", nullable=False)
    pre_period_avg: Mapped[float] = mapped_column(Float, nullable=False)
    post_period_avg: Mapped[float] = mapped_column(Float, nullable=False)
    did_estimate: Mapped[float] = mapped_column(Float, nullable=False)
    p_value: Mapped[float] = mapped_column(Float, default=0.01, nullable=False)
    is_statistically_significant: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    diagnostics_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    observed_at: Mapped[str] = mapped_column(String(50), nullable=False)


class EnterpriseHealthSnapshotModel(AEGISBaseModel):
    """Explainable Enterprise Health Calculation Model."""

    __tablename__ = "enterprise_health_snapshots"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    snapshot_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    overall_status: Mapped[str] = mapped_column(String(50), default="HEALTHY", nullable=False)
    health_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(50), default="AEGIS_Health_v1.0", nullable=False)
    dimensions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    underlying_evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    unavailable_dimensions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)


class ExecutiveReportModel(AEGISBaseModel):
    """Evidence-Backed Executive Intelligence Report Model."""

    __tablename__ = "executive_reports"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    report_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    observed_facts_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    model_predictions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    system_recommendations_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    decisions_executed_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    attributions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    generated_at: Mapped[str] = mapped_column(String(50), nullable=False)


class ScenarioAnalysisModel(AEGISBaseModel):
    """Strategic Decision Scenario Simulation Model."""

    __tablename__ = "scenario_analyses"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    scenario_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    baseline_scenario_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    alternative_scenarios_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    sensitivity_analysis_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recommended_option_id: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)
