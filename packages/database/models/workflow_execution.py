"""Workflow Execution, Human Task, Connector, Trace Event, and Outbox Database Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class WorkflowRunModel(AEGISBaseModel):
    """Workflow Execution Instance Run Model."""

    __tablename__ = "workflow_runs"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    workflow_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    workflow_version_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)  # EVENT, SCHEDULE, API, DECISION, HUMAN
    trigger_payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, RUNNING, COMPLETED, FAILED, TIMED_OUT, CANCELLED, WAITING_HUMAN, COMPENSATING, COMPENSATED, PARTIALLY_COMPENSATED, COMPENSATION_FAILED
    current_step_key: Mapped[str] = mapped_column(String(100), nullable=True)
    workflow_manifest_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    worker_id: Mapped[str] = mapped_column(String(100), nullable=True)
    lease_id: Mapped[str] = mapped_column(String(100), nullable=True)
    lease_expires_at: Mapped[str] = mapped_column(String(50), nullable=True)
    fencing_token: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[str] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[str] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    compensation_status: Mapped[str] = mapped_column(String(50), nullable=True)
    cost_cents: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class WorkflowNodeRunModel(AEGISBaseModel):
    """Workflow DAG Node Execution Run Model."""

    __tablename__ = "workflow_node_runs"

    workflow_run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    node_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, RUNNING, COMPLETED, FAILED, TIMED_OUT, CANCELLED, SKIPPED, WAITING_APPROVAL, WAITING_HUMAN, COMPENSATED, COMPENSATION_FAILED
    inputs_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    outputs_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    started_at: Mapped[str] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[str] = mapped_column(String(50), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    worker_id: Mapped[str] = mapped_column(String(100), nullable=True)
    fencing_token: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    action_contract_id: Mapped[str] = mapped_column(String(100), nullable=True)
    governed_execution_id: Mapped[str] = mapped_column(String(100), nullable=True)
    postcondition_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class WorkflowHumanTaskModel(AEGISBaseModel):
    """Generic Human Form / Action Task Model (Separated from Governance Approval)."""

    __tablename__ = "workflow_human_tasks"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    workflow_run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    node_run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    task_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    assignee: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    role: Mapped[str] = mapped_column(String(100), nullable=True)
    form_schema_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    submitted_data_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, IN_PROGRESS, COMPLETED, REJECTED, ESCALATED, TIMED_OUT
    expires_at: Mapped[str] = mapped_column(String(50), nullable=True)
    escalated_to: Mapped[str] = mapped_column(String(100), nullable=True)
    completed_at: Mapped[str] = mapped_column(String(50), nullable=True)


class WorkflowConnectorModel(AEGISBaseModel):
    """Governed Integration Connector Model storing non-secret config and secret references."""

    __tablename__ = "workflow_connectors"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    connector_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # HTTP, DATABASE, MESSAGE_QUEUE, SERVICE_BUS, CUSTOM
    auth_type: Mapped[str] = mapped_column(String(50), default="NONE", nullable=False)  # API_KEY, OAUTH2, BASIC, MUTUAL_TLS, AWS_IAM, NONE
    non_secret_config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    secret_refs_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    egress_allowlist_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class WorkflowTraceEventModel(AEGISBaseModel):
    """Distributed Lineage Trace Span Event Model."""

    __tablename__ = "workflow_trace_events"

    workflow_run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    node_run_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    trace_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    span_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    parent_span_id: Mapped[str] = mapped_column(String(100), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)


class WorkflowOutboxModel(AEGISBaseModel):
    """Transactional Event Outbox Model."""

    __tablename__ = "workflow_outbox"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, SENT, FAILED
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
