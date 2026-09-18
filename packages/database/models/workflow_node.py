"""Workflow Node and Edge Database Models."""

from sqlalchemy import String, Text, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class WorkflowNodeModel(AEGISBaseModel):
    """Workflow Node Definition Model."""

    __tablename__ = "workflow_nodes"

    workflow_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    workflow_version_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    node_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # ACTION, DECISION, CONDITION, TRANSFORM, WAIT, SCHEDULE, HUMAN_APPROVAL, HUMAN_TASK, NOTIFICATION, SUBWORKFLOW, EVENT_WAIT, VERIFICATION, COMPENSATION
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    action_contract_id: Mapped[str] = mapped_column(String(100), nullable=True)
    action_contract_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=True)
    inputs_schema_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    outputs_schema_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    retry_policy_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    compensation_node_key: Mapped[str] = mapped_column(String(100), nullable=True)
    risk_metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    data_classification: Mapped[str] = mapped_column(String(50), default="INTERNAL", nullable=False)


class WorkflowEdgeModel(AEGISBaseModel):
    """Workflow Edge DAG Connection Model."""

    __tablename__ = "workflow_edges"

    workflow_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    workflow_version_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_node_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_node_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    condition_expression: Mapped[str] = mapped_column(Text, nullable=True)
