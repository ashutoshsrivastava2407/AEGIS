"""Workflow Catalog, Versioning, and Lifecycle Management Registry."""

import hashlib
import json
import uuid
from typing import Dict, Any, List, Optional
from packages.database.models.workflow import WorkflowModel, WorkflowVersionModel
from packages.database.models.workflow_node import WorkflowNodeModel, WorkflowEdgeModel


class WorkflowRegistry:
    """Manages workflow definitions, immutable versioning, SHA-256 fingerprinting, and state transitions."""

    VALID_STATES = {"DRAFT", "VALIDATED", "ACTIVE", "PAUSED", "SUSPENDED", "RETIRED"}

    def compute_definition_fingerprint(self, graph_json: Dict[str, Any], node_contracts_json: Dict[str, Any]) -> str:
        """Compute authoritative SHA-256 fingerprint of the immutable workflow definition graph."""
        canonical_str = json.dumps(
            {"graph": graph_json, "node_contracts": node_contracts_json},
            sort_keys=True
        )
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def create_workflow(
        self,
        name: str,
        description: str,
        owner: str,
        business_domain: str = "ENTERPRISE",
        tenant_id: str = "default",
        trigger_type: str = "MANUAL",
        risk_profile: str = "MEDIUM_RISK",
        timeout_policy_json: Optional[Dict[str, Any]] = None,
        retry_policy_json: Optional[Dict[str, Any]] = None,
        compensation_policy_json: Optional[Dict[str, Any]] = None,
    ) -> WorkflowModel:
        """Create a new Workflow master definition in DRAFT status."""
        workflow_id = str(uuid.uuid4())
        return WorkflowModel(
            id=workflow_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            owner=owner,
            business_domain=business_domain,
            version=1,
            status="DRAFT",
            trigger_type=trigger_type,
            risk_profile=risk_profile,
            timeout_policy_json=timeout_policy_json or {"default_timeout_seconds": 300, "max_workflow_timeout_seconds": 3600},
            retry_policy_json=retry_policy_json or {"max_retries": 3, "backoff_coefficient": 2.0, "initial_interval_seconds": 2},
            compensation_policy_json=compensation_policy_json or {"enabled": True, "mode": "REVERSE_ORDER"},
            active_version_id=None,
            created_by=owner,
            updated_by=owner,
        )

    def publish_version(
        self,
        workflow: WorkflowModel,
        graph_json: Dict[str, Any],
        node_contracts_json: Dict[str, Any],
        created_by: str = "system",
    ) -> WorkflowVersionModel:
        """Publish a new immutable WorkflowVersionModel, compute fingerprint, and mark active if valid."""
        fingerprint = self.compute_definition_fingerprint(graph_json, node_contracts_json)
        version_id = str(uuid.uuid4())
        next_version_num = workflow.version + 1 if workflow.active_version_id else 1

        version_model = WorkflowVersionModel(
            id=version_id,
            tenant_id=workflow.tenant_id,
            workflow_id=workflow.id,
            version_number=next_version_num,
            definition_fingerprint=fingerprint,
            graph_json=graph_json,
            node_contracts_json=node_contracts_json,
            is_active=True,
            is_frozen=True,
            status="ACTIVE",
            created_by=created_by,
            updated_by=created_by,
        )

        workflow.version = next_version_num
        workflow.active_version_id = version_id
        workflow.status = "ACTIVE"
        workflow.updated_by = created_by

        return version_model

    def transition_state(self, workflow: WorkflowModel, target_state: str, updated_by: str = "system") -> WorkflowModel:
        """Enforce state transition machine rules."""
        target_state = target_state.upper()
        if target_state not in self.VALID_STATES:
            raise ValueError(f"Invalid workflow state: {target_state}. Must be one of {self.VALID_STATES}")

        current = workflow.status
        allowed = {
            "DRAFT": {"VALIDATED", "RETIRED"},
            "VALIDATED": {"ACTIVE", "DRAFT", "RETIRED"},
            "ACTIVE": {"PAUSED", "SUSPENDED", "RETIRED"},
            "PAUSED": {"ACTIVE", "RETIRED"},
            "SUSPENDED": {"ACTIVE", "RETIRED"},
            "RETIRED": set(),
        }

        if target_state not in allowed.get(current, set()):
            raise ValueError(f"Illegal workflow state transition from {current} to {target_state}")

        workflow.status = target_state
        workflow.updated_by = updated_by
        return workflow
