"""Formal Versioned Action Contract Registry for AEGIS Decision Actions."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ActionContract:
    """Versioned Action Contract definition."""

    action_type: str
    contract_version: str = "1.0.0"
    input_schema: Dict[str, Any] = field(default_factory=dict)
    required_permissions: List[str] = field(default_factory=list)
    risk_tier: str = "MEDIUM_RISK"
    side_effects: List[str] = field(default_factory=list)
    reversibility: str = "REVERSIBLE"
    idempotency_required: bool = True
    timeout_seconds: int = 30
    retry_limit: int = 3
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    compensation_action: Optional[str] = None
    allowed_environments: List[str] = field(default_factory=lambda: ["production", "staging", "development"])


class ActionContractRegistry:
    """Registry maintaining versioned Action Contracts across AEGIS."""

    def __init__(self):
        self._contracts: Dict[str, Dict[str, ActionContract]] = {}
        self._register_default_contracts()

    def register(self, contract: ActionContract) -> None:
        """Register an action contract."""
        if contract.action_type not in self._contracts:
            self._contracts[contract.action_type] = {}
        self._contracts[contract.action_type][contract.contract_version] = contract

    def get_contract(self, action_type: str, contract_version: str = "1.0.0") -> Optional[ActionContract]:
        """Retrieve a specific versioned action contract."""
        versions = self._contracts.get(action_type, {})
        if contract_version in versions:
            return versions[contract_version]
        # Fallback to latest available version if requested version absent
        if versions:
            latest_ver = sorted(versions.keys())[-1]
            return versions[latest_ver]
        return None

    def validate_action(self, action_type: str, parameters: Dict[str, Any], contract_version: str = "1.0.0") -> Dict[str, Any]:
        """Validate action parameters against action contract."""
        contract = self.get_contract(action_type, contract_version)
        if not contract:
            return {"valid": False, "error": f"Action contract not found for type '{action_type}' version '{contract_version}'"}
        
        # Check required fields in schema
        required_fields = contract.input_schema.get("required", [])
        missing = [f for f in required_fields if f not in parameters]
        if missing:
            return {"valid": False, "error": f"Missing required parameters: {missing}"}
        
        return {"valid": True, "contract": contract}

    def _register_default_contracts(self) -> None:
        """Register default core AEGIS decision action contracts."""
        # 1. System Scaling Contract
        self.register(ActionContract(
            action_type="SCALE_SERVICE_WORKERS",
            contract_version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["service_name", "target_replicas"],
                "properties": {
                    "service_name": {"type": "string"},
                    "target_replicas": {"type": "integer"}
                }
            },
            required_permissions=["system:write"],
            risk_tier="MEDIUM_RISK",
            side_effects=["MODIFIES_INFRASTRUCTURE"],
            reversibility="REVERSIBLE",
            preconditions=["target_replicas >= 1"],
            postconditions=["service_replicas == target_replicas"],
            compensation_action="RESTORE_PREVIOUS_REPLICAS"
        ))

        # 2. Database Index Maintenance Contract
        self.register(ActionContract(
            action_type="REBUILD_DATABASE_INDEX",
            contract_version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["table_name", "index_name"],
                "properties": {
                    "table_name": {"type": "string"},
                    "index_name": {"type": "string"}
                }
            },
            required_permissions=["db:admin"],
            risk_tier="HIGH_RISK",
            side_effects=["LOCKS_RESOURCE_TEMPORARILY"],
            reversibility="REVERSIBLE",
            preconditions=["table_exists == True"],
            postconditions=["index_status == 'VALID'"]
        ))

        # 3. Regional Traffic Reroute Contract
        self.register(ActionContract(
            action_type="REROUTE_REGIONAL_TRAFFIC",
            contract_version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["source_region", "target_region", "percentage"],
                "properties": {
                    "source_region": {"type": "string"},
                    "target_region": {"type": "string"},
                    "percentage": {"type": "number"}
                }
            },
            required_permissions=["network:write"],
            risk_tier="CRITICAL_RISK",
            side_effects=["MODIFIES_NETWORK_ROUTING"],
            reversibility="REVERSIBLE",
            preconditions=["source_region != target_region"],
            postconditions=["traffic_diverted == True"],
            compensation_action="RESET_TRAFFIC_ROUTING"
        ))

        # 4. Operational Remediation Contracts
        for action_name in ["RESTART_POD", "RESTART_SERVICE", "CLEAR_CACHE_POOL", "DRAIN_CLUSTER"]:
            self.register(ActionContract(
                action_type=action_name,
                contract_version="1.0.0",
                input_schema={"type": "object"},
                required_permissions=["system:write"],
                risk_tier="MEDIUM_RISK",
                side_effects=["RESTARTS_RESOURCE"],
                reversibility="REVERSIBLE",
                postconditions=[],
            ))
