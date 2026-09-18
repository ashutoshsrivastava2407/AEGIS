"""Production Operations, Observability, Reliability, Incident Management, Recovery, Deployment, and FinOps Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class ServiceCatalogModel(AEGISBaseModel):
    """Service Catalog & Ownership Model."""

    __tablename__ = "service_catalog"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_team: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tier: Mapped[str] = mapped_column(String(50), default="TIER_1", nullable=False)  # TIER_0, TIER_1, TIER_2, TIER_3
    criticality: Mapped[str] = mapped_column(String(50), default="CRITICAL", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    environment: Mapped[str] = mapped_column(String(50), default="PRODUCTION", nullable=False, index=True)
    escalation_policy: Mapped[str] = mapped_column(String(100), nullable=False)
    repo_url: Mapped[str] = mapped_column(String(255), nullable=True)


class ProductionReadinessModel(AEGISBaseModel):
    """Production Readiness & Operational Checklist Model."""

    __tablename__ = "production_readiness"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    readiness_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    slo_coverage: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    backup_coverage: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observability_coverage: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    security_controls_passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    dr_readiness_passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    checklist_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class ServiceHealthModel(AEGISBaseModel):
    """Service Health, Liveness, and Readiness Probe Status Model."""

    __tablename__ = "service_health"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="HEALTHY", nullable=False, index=True)  # HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN
    liveness: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    readiness: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    startup: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    active_version: Mapped[str] = mapped_column(String(50), default="v1.0.0", nullable=False)
    last_probe_at: Mapped[str] = mapped_column(String(50), nullable=False)


class ServiceDependencyModel(AEGISBaseModel):
    """Machine-Readable Service Dependency Graph Model."""

    __tablename__ = "service_dependencies"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    source_service: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_dependency: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    dependency_type: Mapped[str] = mapped_column(String(50), default="SYNCHRONOUS", nullable=False)  # SYNCHRONOUS, ASYNCHRONOUS, DATABASE, STORAGE
    impact_tier: Mapped[str] = mapped_column(String(50), default="CRITICAL", nullable=False)
    is_hard_dependency: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SLOModel(AEGISBaseModel):
    """Service Level Objective (SLO) Definition Model."""

    __tablename__ = "service_slos"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    slo_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)  # AVAILABILITY, LATENCY, ERROR_RATE, THROUGHPUT
    target_percent: Mapped[float] = mapped_column(Float, default=99.9, nullable=False)
    window_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    current_performance: Mapped[float] = mapped_column(Float, default=99.95, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="MET", nullable=False)  # MET, AT_RISK, BREACHED


class ErrorBudgetModel(AEGISBaseModel):
    """SLO Error Budget Burn Rate & Remaining Budget Model."""

    __tablename__ = "error_budgets"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    slo_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    budget_remaining_percent: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    consumed_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    short_window_burn_rate: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    long_window_burn_rate: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    budget_status: Mapped[str] = mapped_column(String(50), default="HEALTHY", nullable=False)  # HEALTHY, WARNING, EXHAUSTED


class IncidentModel(AEGISBaseModel):
    """First-Class Operational Incident Lifecycle Model."""

    __tablename__ = "incidents"

    incident_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="SEV2", nullable=False, index=True)  # SEV0, SEV1, SEV2, SEV3, SEV4
    status: Mapped[str] = mapped_column(String(50), default="DETECTED", nullable=False, index=True)  # DETECTED, TRIAGED, MITIGATING, MONITORING, RESOLVED, CLOSED
    owner_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    incident_commander: Mapped[str] = mapped_column(String(100), nullable=False)
    affected_services_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    linked_alerts_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    detected_at: Mapped[str] = mapped_column(String(50), nullable=False)
    resolved_at: Mapped[str] = mapped_column(String(50), nullable=True)


class IncidentTimelineEventModel(AEGISBaseModel):
    """Operational Incident Audit Timeline Event Model."""

    __tablename__ = "incident_timeline_events"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    incident_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # DETECTED, SEVERITY_CHANGED, RESPONDER_ADDED, MITIGATION_STARTED, RESOLVED, POSTMORTEM_CREATED
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)


class RunbookModel(AEGISBaseModel):
    """Standardized Operational Runbook Model."""

    __tablename__ = "runbooks"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    runbook_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # DATABASE, WORKER, BROKER, LLM, SERVICE, SECURITY
    detection_procedure: Mapped[str] = mapped_column(Text, nullable=False)
    diagnosis_steps: Mapped[str] = mapped_column(Text, nullable=False)
    mitigation_steps: Mapped[str] = mapped_column(Text, nullable=False)
    verification_steps: Mapped[str] = mapped_column(Text, nullable=False)
    governed_action_name: Mapped[str] = mapped_column(String(100), nullable=True)


class DurableRemediationEvidenceModel(AEGISBaseModel):
    """Immutable Audit Evidence Record for Policy-Governed Automated Remediations."""

    __tablename__ = "durable_remediation_evidence"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    remediation_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    trigger_alert_id: Mapped[str] = mapped_column(String(100), nullable=False)
    target_service: Mapped[str] = mapped_column(String(100), nullable=False)
    action_contract_id: Mapped[str] = mapped_column(String(100), nullable=False)
    governance_decision_id: Mapped[str] = mapped_column(String(36), nullable=False)
    policy_evaluation_id: Mapped[str] = mapped_column(String(36), nullable=False)
    before_state_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    after_state_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    verification_result: Mapped[str] = mapped_column(String(50), default="VERIFIED_SUCCESS", nullable=False)
    executed_at: Mapped[str] = mapped_column(String(50), nullable=False)


class DeploymentModel(AEGISBaseModel):
    """Deployment Release Tracking with Immutable Release Artifact Identity."""

    __tablename__ = "deployments"

    deployment_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    release_version: Mapped[str] = mapped_column(String(50), nullable=False)
    artifact_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    environment: Mapped[str] = mapped_column(String(50), default="PRODUCTION", nullable=False)
    config_version: Mapped[str] = mapped_column(String(50), nullable=False)
    policy_version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    rollout_strategy: Mapped[str] = mapped_column(String(50), default="CANARY", nullable=False)  # CANARY, BLUE_GREEN, ROLLING
    status: Mapped[str] = mapped_column(String(50), default="PROMOTED", nullable=False, index=True)  # IN_PROGRESS, HEALTH_CHECKING, PROMOTED, ROLLED_BACK, FAILED
    deployed_by: Mapped[str] = mapped_column(String(100), nullable=False)
    deployed_at: Mapped[str] = mapped_column(String(50), nullable=False)


class FeatureFlagModel(AEGISBaseModel):
    """Controlled Feature Flag & Rollout Percentage Model."""

    __tablename__ = "feature_flags"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    flag_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rollout_percentage: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    target_environment: Mapped[str] = mapped_column(String(50), default="PRODUCTION", nullable=False)


class ChangeRecordModel(AEGISBaseModel):
    """Operational Change Management Record Model."""

    __tablename__ = "change_records"

    change_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)  # DEPLOYMENT, CONFIGURATION, POLICY_CHANGE, INFRASTRUCTURE
    requester_id: Mapped[str] = mapped_column(String(100), nullable=False)
    approver_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="IMPLEMENTED", nullable=False)  # REQUESTED, APPROVED, IMPLEMENTED, ROLLED_BACK
    implemented_at: Mapped[str] = mapped_column(String(50), nullable=False)


class BackupModel(AEGISBaseModel):
    """Database, Storage, Policy, and Workflow Backup Metadata Model."""

    __tablename__ = "backups"

    backup_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    backup_type: Mapped[str] = mapped_column(String(50), nullable=False)  # DATABASE, OBJECT_STORAGE, POLICY_STATE, WORKFLOW_STATE
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)


class RestoreJobModel(AEGISBaseModel):
    """Restore Verification & Data Consistency Check Job Model."""

    __tablename__ = "restore_jobs"

    restore_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    backup_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    schema_check_passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_consistency_passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    functional_smoke_test_passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="VERIFIED_SUCCESS", nullable=False)
    verified_at: Mapped[str] = mapped_column(String(50), nullable=False)


class RecoveryPointModel(AEGISBaseModel):
    """Disaster Recovery Target vs Measured RPO / RTO Metrics Model."""

    __tablename__ = "recovery_points"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    target_rpo_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    measured_rpo_minutes: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    target_rto_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    measured_rto_minutes: Mapped[float] = mapped_column(Float, default=12.0, nullable=False)
    dr_readiness_status: Mapped[str] = mapped_column(String(50), default="READY", nullable=False)
    last_dr_test_at: Mapped[str] = mapped_column(String(50), nullable=False)


class PlatformCostEventModel(AEGISBaseModel):
    """Platform-Wide FinOps Cost Attribution Event Model."""

    __tablename__ = "platform_cost_events"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    business_domain: Mapped[str] = mapped_column(String(100), default="INFRASTRUCTURE", nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    workload_type: Mapped[str] = mapped_column(String(50), nullable=False)  # DATABASE, LLM, WORKFLOW, AGENT, ML, COMPUTATION
    workload_id: Mapped[str] = mapped_column(String(100), nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)


class CostBudgetModel(AEGISBaseModel):
    """Tenant & Service FinOps Budget Model."""

    __tablename__ = "cost_budgets"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    budget_name: Mapped[str] = mapped_column(String(100), nullable=False)
    monthly_budget_usd: Mapped[float] = mapped_column(Float, default=5000.0, nullable=False)
    actual_spend_usd: Mapped[float] = mapped_column(Float, default=1200.0, nullable=False)
    forecast_spend_usd: Mapped[float] = mapped_column(Float, default=3400.0, nullable=False)
    variance_usd: Mapped[float] = mapped_column(Float, default=-1600.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="UNDER_BUDGET", nullable=False)


class CostAnomalyFindingModel(AEGISBaseModel):
    """FinOps Cost Anomaly Finding Model."""

    __tablename__ = "cost_anomaly_findings"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    anomaly_title: Mapped[str] = mapped_column(String(255), nullable=False)
    affected_service: Mapped[str] = mapped_column(String(100), nullable=False)
    expected_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    observed_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    spike_multiplier: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False)
